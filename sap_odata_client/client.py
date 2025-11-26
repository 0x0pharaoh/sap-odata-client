import time
from typing import Dict, Any, Tuple
import httpx


class SAPClient:
    """
    Lightweight async SAP S/4HANA Sales Order OData client.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str,
        api_base: str,
        sales_endpoint: str = (
            "/sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder"
        ),
        timeout: int = 30,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.api_base = api_base.rstrip("/")
        self.sales_endpoint = sales_endpoint

        self._token = None
        self._token_expiry = 0

        self.http = httpx.AsyncClient(timeout=timeout)

    async def _get_oauth_token(self) -> str:
        now = int(time.time())
        if self._token and now < self._token_expiry - 30:
            return self._token

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        resp = await self.http.post(
            self.token_url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()

        json_data = resp.json()
        self._token = json_data["access_token"]
        self._token_expiry = now + json_data.get("expires_in", 3600)
        return self._token

    async def _get_csrf_token_and_cookies(
        self,
        token: str,
    ) -> Tuple[str, httpx.Cookies]:
        url = (
            f"{self.api_base}/sap/opu/odata/sap/"
            "API_SALES_ORDER_SRV"
        )

        resp = await self.http.get(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "x-csrf-token": "fetch",
                "Accept": "application/json",
            },
        )
        resp.raise_for_status()

        csrf = resp.headers.get("x-csrf-token")
        return csrf, resp.cookies

    async def create_sales_order(
        self,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        token = await self._get_oauth_token()
        csrf, cookies = await self._get_csrf_token_and_cookies(token)

        # Assign cookies to the client (fixes DeprecationWarning)
        self.http.cookies = cookies

        url = f"{self.api_base}{self.sales_endpoint}"

        resp = await self.http.post(
            url,
            json=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "x-csrf-token": csrf or "",
                "Accept": "application/json",
            },
        )
        resp.raise_for_status()

        return resp.json()
