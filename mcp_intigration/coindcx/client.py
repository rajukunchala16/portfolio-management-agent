from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any

import httpx
from dotenv import load_dotenv
import os

from config import config

load_dotenv()


class CoinDCXError(Exception):
    """Base CoinDCX exception."""


class CoinDCXAuthenticationError(CoinDCXError):
    """Authentication failure."""


class CoinDCXAPIError(CoinDCXError):
    """CoinDCX API failure."""


class CoinDCXClient:
    """
    Async CoinDCX REST API client.

    Responsible for:
    - authentication
    - HMAC signature generation
    - HTTP communication
    - response validation

    MCP should not know how CoinDCX authentication works.
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
    ) -> None:

        self.api_key = api_key or os.getenv("COINDCX_API_KEY")
        self.api_secret = api_secret or os.getenv("COINDCX_API_SECRET")

        self.base_url = (
            base_url
            or config["coindcx"]["coindcx_base_url"]
        ).rstrip("/")

        self.timeout = timeout or float(
            config["coindcx"]["coindcx_timeout"]
        )

        if not self.api_key:
            raise ValueError("COINDCX_API_KEY is not configured")

        if not self.api_secret:
            raise ValueError("COINDCX_API_SECRET is not configured")

        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    @staticmethod
    def _timestamp() -> int:
        return int(time.time() * 1000)

    def _sign(self, payload: str) -> str:
        return hmac.new(
            self.api_secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _authenticated_headers(self, body: dict[str, Any]) -> dict[str, str]:

        payload = json.dumps(
            body,
            separators=(",", ":"),
        )

        signature = self._sign(payload)

        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-AUTH-APIKEY": self.api_key,
            "X-AUTH-SIGNATURE": signature,
        }

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    async def _get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> Any:

        url = f"{self.base_url}{endpoint}"

        response = await self.client.get(
            url,
            params=params,
        )

        return self._handle_response(response)

    async def _post_private(
        self,
        endpoint: str,
        body: dict[str, Any] | None = None,
    ) -> Any:

        body = body or {}

        body["timestamp"] = self._timestamp()

        payload = json.dumps(
            body,
            separators=(",", ":"),
        )

        headers = self._authenticated_headers(body)

        url = f"{self.base_url}{endpoint}"

        response = await self.client.post(
            url,
            content=payload,
            headers=headers,
        )

        return self._handle_response(response)

    @staticmethod
    def _handle_response(response: httpx.Response) -> Any:

        if response.status_code in (401, 403):
            raise CoinDCXAuthenticationError(
                f"CoinDCX authentication failed: {response.text}"
            )

        if response.status_code >= 400:
            raise CoinDCXAPIError(
                f"CoinDCX API error "
                f"{response.status_code}: {response.text}"
            )

        try:
            return response.json()
        except Exception as exc:
            raise CoinDCXAPIError(
                "CoinDCX returned invalid JSON"
            ) from exc

    # ------------------------------------------------------------------
    # Public APIs
    # ------------------------------------------------------------------

    async def get_markets(self) -> Any:
        """
        Return currently active markets.
        """
        return await self._get(
            "/exchange/v1/markets"
        )

    async def get_market_details(self) -> Any:
        """
        Return market metadata such as:
        - precision
        - min quantity
        - max quantity
        - order types
        - exchange code
        """
        return await self._get(
            "/exchange/v1/markets_details"
        )

    async def get_ticker(self) -> Any:
        """
        Return current market ticker information.
        """
        return await self._get(
            "/exchange/ticker"
        )

    async def get_trade_history(
        self,
        pair: str,
        limit: int = 50,
    ) -> Any:
        """
        Return public market trade history.
        """

        if limit < 1 or limit > 1000:
            raise ValueError("limit must be between 1 and 1000")

        return await self._get(
            "/market_data/trade_history",
            params={
                "pair": pair,
                "limit": limit,
            },
        )

    async def get_candles(
        self,
        pair: str,
        interval: str = "1m",
    ) -> Any:
        """
        Return OHLC candle data.
        """

        allowed_intervals = {
            "1m",
            "5m",
            "15m",
            "30m",
            "1h",
            "2h",
            "4h",
            "6h",
            "8h",
            "1d",
        }

        if interval not in allowed_intervals:
            raise ValueError(
                f"Unsupported interval: {interval}"
            )

        return await self._get(
            "/market_data/candles",
            params={
                "pair": pair,
                "interval": interval,
            },
        )

    # ------------------------------------------------------------------
    # Account APIs
    # ------------------------------------------------------------------

    async def get_balances(self) -> Any:
        """
        Retrieve spot account balances.
        """

        return await self._post_private(
            "/exchange/v1/users/balances"
        )

    async def get_user_info(self) -> Any:
        """
        Retrieve CoinDCX user information.
        """

        return await self._post_private(
            "/exchange/v1/users/info"
        )

    # ------------------------------------------------------------------
    # Orders
    # ------------------------------------------------------------------

    async def get_active_orders(
        self,
        market: str,
        side: str | None = None,
        page: int = 1,
        size: int = 200,
    ) -> Any:

        if side and side not in {"buy", "sell"}:
            raise ValueError(
                "side must be buy or sell"
            )

        if page < 1:
            raise ValueError(
                "page must be >= 1"
            )

        if size < 1 or size > 200:
            raise ValueError(
                "size must be between 1 and 200"
            )

        body: dict[str, Any] = {
            "market": market,
            "page": page,
            "size": size,
        }

        if side:
            body["side"] = side

        return await self._post_private(
            "/exchange/v1/orders/active_orders",
            body,
        )

    async def get_order_status(
        self,
        order_id: str | None = None,
        client_order_id: str | None = None,
    ) -> Any:

        if not order_id and not client_order_id:
            raise ValueError(
                "order_id or client_order_id is required"
            )

        body: dict[str, Any] = {}

        if order_id:
            body["id"] = int(order_id)

        if client_order_id:
            body["client_order_id"] = client_order_id

        return await self._post_private(
            "/exchange/v1/orders/status",
            body,
        )

    async def get_account_trade_history(
        self,
        symbol: str | None = None,
        limit: int = 100,
        sort: str = "desc",
    ) -> Any:

        if limit < 1 or limit > 500:
            raise ValueError(
                "limit must be between 1 and 500"
            )

        if sort not in {"asc", "desc"}:
            raise ValueError(
                "sort must be asc or desc"
            )

        body: dict[str, Any] = {
            "limit": limit,
            "sort": sort,
        }

        if symbol:
            body["symbol"] = symbol

        return await self._post_private(
            "/exchange/v1/orders/trade_history",
            body,
        )

    # ------------------------------------------------------------------
    # Trading
    # ------------------------------------------------------------------

    async def create_order(
        self,
        market: str,
        side: str,
        order_type: str,
        total_quantity: float,
        price_per_unit: float | None = None,
        client_order_id: str | None = None,
    ) -> Any:

        trading_enabled = (
            os.getenv(
                "ENABLE_TRADING",
                "false",
            ).lower()
            == "true"
        )

        if not trading_enabled:
            raise PermissionError(
                "Trading is disabled. "
                "Set ENABLE_TRADING=true only after "
                "implementing your own production approval controls."
            )

        if side not in {"buy", "sell"}:
            raise ValueError(
                "side must be buy or sell"
            )

        allowed_order_types = {
            "market_order",
            "limit_order",
            "stop_limit",
            "take_profit_limit",
        }

        if order_type not in allowed_order_types:
            raise ValueError(
                f"Unsupported order type: {order_type}"
            )

        if total_quantity <= 0:
            raise ValueError(
                "total_quantity must be greater than 0"
            )

        if (
            order_type != "market_order"
            and price_per_unit is None
        ):
            raise ValueError(
                "price_per_unit is required "
                "for non-market orders"
            )

        body: dict[str, Any] = {
            "market": market,
            "side": side,
            "order_type": order_type,
            "total_quantity": total_quantity,
        }

        if price_per_unit is not None:
            body["price_per_unit"] = price_per_unit

        if client_order_id:
            body["client_order_id"] = client_order_id

        return await self._post_private(
            "/exchange/v1/orders/create",
            body,
        )

    async def cancel_order(
        self,
        order_id: str | None = None,
        client_order_id: str | None = None,
    ) -> Any:

        if not order_id and not client_order_id:
            raise ValueError(
                "order_id or client_order_id is required"
            )

        body: dict[str, Any] = {}

        if order_id:
            body["id"] = int(order_id)

        if client_order_id:
            body["client_order_id"] = client_order_id

        return await self._post_private(
            "/exchange/v1/orders/cancel_by_ids",
            body,
        )

    async def close(self) -> None:
        await self.client.aclose()