import pytest
import respx
from httpx import Response
from sap_odata_client import SAPClient


@pytest.mark.asyncio
async def test_oauth_failure():
    client = SAPClient(
        client_id="wrong",
        client_secret="wrong",
        token_url="https://auth.example.com/oauth/token",
        api_base="https://api.example.com",
    )

    respx.post("https://auth.example.com/oauth/token").mock(
        return_value=Response(401, json={"error": "invalid_client"})
    )

    with pytest.raises(Exception):
        await client.create_sales_order({})
