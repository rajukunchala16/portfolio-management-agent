from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from mcp_intigration.coindcx.client import (
    CoinDCXClient,
    CoinDCXError,
)


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger(
    "coindcx-mcp-server"
)


# ---------------------------------------------------------
# MCP Server
# ---------------------------------------------------------

mcp = FastMCP(
    "CoinDCX MCP Server",
    json_response=True,
)


client = CoinDCXClient()


# =========================================================
# PUBLIC MARKET TOOLS
# =========================================================

@mcp.tool()
async def get_markets() -> Any:
    """
    Get all currently active CoinDCX markets.

    Use this before trading when the agent needs to
    validate whether a market exists.
    """

    logger.info(
        "MCP tool called: get_markets"
    )

    return await client.get_markets()


@mcp.tool()
async def get_market_details() -> Any:
    """
    Get CoinDCX market metadata.

    Includes:
    - precision
    - min quantity
    - max quantity
    - min notional
    - order types
    - exchange code
    - pair information
    """

    logger.info(
        "MCP tool called: get_market_details"
    )

    return await client.get_market_details()


@mcp.tool()
async def get_ticker() -> Any:
    """
    Get current CoinDCX market ticker data.

    Includes bid, ask, high, low and volume.
    """

    logger.info(
        "MCP tool called: get_ticker"
    )

    return await client.get_ticker()


@mcp.tool()
async def get_market_trade_history(
    pair: str,
    limit: int = 50,
) -> Any:
    """
    Get public trade history for a CoinDCX market.

    Example pair:
    B-BTC_USDT
    """

    logger.info(
        "Getting public trade history: %s",
        pair,
    )

    return await client.get_trade_history(
        pair=pair,
        limit=limit,
    )


@mcp.tool()
async def get_candles(
    pair: str,
    interval: str = "1m",
) -> Any:
    """
    Get OHLC candles for a CoinDCX market.

    Example:
    pair=B-BTC_USDT
    interval=1h
    """

    logger.info(
        "Getting candles: pair=%s interval=%s",
        pair,
        interval,
    )

    return await client.get_candles(
        pair=pair,
        interval=interval,
    )


# =========================================================
# ACCOUNT TOOLS
# =========================================================

@mcp.tool()
async def get_balances() -> Any:
    """
    Get the authenticated CoinDCX spot account balances.

    Returns available and locked balances.
    """

    logger.info(
        "MCP tool called: get_balances"
    )

    return await client.get_balances()


@mcp.tool()
async def get_user_info() -> Any:
    """
    Get authenticated CoinDCX user information.
    """

    logger.info(
        "MCP tool called: get_user_info"
    )

    return await client.get_user_info()


# =========================================================
# ORDER TOOLS
# =========================================================

@mcp.tool()
async def get_active_orders(
    market: str,
    side: str | None = None,
    page: int = 1,
    size: int = 200,
) -> Any:
    """
    Get active/open orders for a CoinDCX market.

    Example:
    market=BTCINR
    side=buy
    """

    logger.info(
        "Getting active orders: "
        "market=%s side=%s",
        market,
        side,
    )

    return await client.get_active_orders(
        market=market,
        side=side,
        page=page,
        size=size,
    )


@mcp.tool()
async def get_order_status(
    order_id: str | None = None,
    client_order_id: str | None = None,
) -> Any:
    """
    Get the status of a CoinDCX order.

    Provide either:
    - order_id
    - client_order_id
    """

    logger.info(
        "Getting order status: order_id=%s "
        "client_order_id=%s",
        order_id,
        client_order_id,
    )

    return await client.get_order_status(
        order_id=order_id,
        client_order_id=client_order_id,
    )


@mcp.tool()
async def get_account_trade_history(
    symbol: str | None = None,
    limit: int = 100,
    sort: str = "desc",
) -> Any:
    """
    Get authenticated account trade history.

    Can optionally filter by symbol.
    """

    logger.info(
        "Getting account trade history: "
        "symbol=%s",
        symbol,
    )

    return await client.get_account_trade_history(
        symbol=symbol,
        limit=limit,
        sort=sort,
    )


# =========================================================
# WRITE / TRADING TOOLS
# =========================================================

@mcp.tool()
async def place_order(
    market: str,
    side: str,
    order_type: str,
    total_quantity: float,
    price_per_unit: float | None = None,
    client_order_id: str | None = None,
    confirm: bool = True,
) -> Any:
    """
    Place a CoinDCX spot order.

    IMPORTANT:
    Trading must be explicitly enabled in the MCP server
    environment.

    The caller must also provide confirm=true.

    Supported order types:
    - market_order
    - limit_order
    - stop_limit
    - take_profit_limit
    """

    if not confirm:
        raise PermissionError(
            "Order was NOT placed. "
            "Explicit confirm=true is required."
        )

    logger.warning(
        "TRADING TOOL CALLED: "
        "market=%s side=%s type=%s quantity=%s",
        market,
        side,
        order_type,
        total_quantity,
    )

    return await client.create_order(
        market=market,
        side=side,
        order_type=order_type,
        total_quantity=total_quantity,
        price_per_unit=price_per_unit,
        client_order_id=client_order_id,
    )


@mcp.tool()
async def cancel_order(
    order_id: str | None = None,
    client_order_id: str | None = None,
    confirm: bool = True,
) -> Any:
    """
    Cancel an active CoinDCX order.

    Explicit confirmation is required.
    """

    if not confirm:
        raise PermissionError(
            "Order was NOT cancelled. "
            "Explicit confirm=true is required."
        )

    logger.warning(
        "CANCEL ORDER TOOL CALLED: "
        "order_id=%s client_order_id=%s",
        order_id,
        client_order_id,
    )

    return await client.cancel_order(
        order_id=order_id,
        client_order_id=client_order_id,
    )


# =========================================================
# SERVER ENTRYPOINT
# =========================================================

if __name__ == "__main__":

    logger.info(
        "Starting CoinDCX MCP server..."
    )

    mcp.run(
        transport="stdio"
    )