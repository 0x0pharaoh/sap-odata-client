import pytest
import respx
from httpx import Response
from sap_odata_client import SAPClient


@pytest.mark.asyncio
@respx.mock
async def test_create_sales_order_success():
    client = SAPClient(
        client_id="id123",
        client_secret="secret123",
        token_url="https://auth.example.com/oauth/token",
        api_base="https://api.example.com",
    )

    # Mock OAuth token request
    respx.post("https://auth.example.com/oauth/token").mock(
        return_value=Response(
            200,
            json={"access_token": "token123", "expires_in": 3600},
        )
    )

    # Mock CSRF token fetch
    respx.get("https://api.example.com/sap/opu/odata/sap/API_SALES_ORDER_SRV").mock(
        return_value=Response(
            200,
            headers={"x-csrf-token": "csrf123"},
            json={"d": {}},
        )
    )

    # Mock create sales order POST
    respx.post(
        "https://api.example.com/sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder"
    ).mock(
        return_value=Response(
            201,
            json={"d": {"SalesOrder": "50000001"}},
        )
    )

    result = await client.create_sales_order({"key": "value"})

    assert result["d"]["SalesOrder"] == "50000001"
