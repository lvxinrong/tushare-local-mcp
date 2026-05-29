from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from mcp.server.fastmcp import FastMCP

from .config import Settings


class DailyClient(Protocol):
    async def daily(
        self,
        ts_code: str,
        start_date: str | None,
        end_date: str | None,
    ) -> list[dict[str, Any]]:
        pass

    async def realtime(self, ts_code: str) -> dict[str, Any]:
        pass

    async def index_realtime(self, index_code: str) -> dict[str, Any]:
        pass

    async def rt_min(
        self,
        ts_code: str,
        freq: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        pass

    async def daily_bars(self, ts_code: str, bars: int) -> list[dict[str, Any]]:
        pass

    async def index_daily_bars(
        self,
        index_code: str,
        bars: int,
    ) -> list[dict[str, Any]]:
        pass

    async def moneyflow(self, ts_code: str, days: int) -> list[dict[str, Any]]:
        pass

    async def hsgt_flow(self, days: int) -> list[dict[str, Any]]:
        pass

    async def fina_indicator(
        self,
        ts_code: str,
        quarters: int,
    ) -> list[dict[str, Any]]:
        pass

    async def income(self, ts_code: str, quarters: int) -> list[dict[str, Any]]:
        pass

    async def stock_basic(self, ts_code: str) -> dict[str, Any]:
        pass


def health_check(settings: Settings) -> dict[str, Any]:
    return {
        "status": "ok",
        "service": settings.name,
        "transport": settings.transport,
        "tushare_token_configured": bool(settings.tushare_token),
    }


def _require_code(value: str, field_name: str) -> str:
    code = value.strip()
    if not code:
        raise ValueError(f"{field_name} must not be blank")
    return code


def _require_positive(value: int, field_name: str) -> int:
    if value <= 0:
        raise ValueError(f"{field_name} must be greater than 0")
    return value


def _require_between(value: int, field_name: str, minimum: int, maximum: int) -> int:
    if value < minimum or value > maximum:
        raise ValueError(f"{field_name} must be between {minimum} and {maximum}")
    return value


def _require_choice(value: str, field_name: str, choices: set[str]) -> str:
    normalized = value.strip().upper()
    if normalized not in choices:
        allowed = ", ".join(sorted(choices))
        raise ValueError(f"{field_name} must be one of: {allowed}")
    return normalized


async def stock_daily(
    ts_code: str,
    start_date: str | None = None,
    end_date: str | None = None,
    *,
    client_factory: Callable[[], DailyClient],
) -> list[dict[str, Any]]:
    client = client_factory()
    ts_code = _require_code(ts_code, "ts_code")
    return await client.daily(ts_code, start_date, end_date)


async def get_realtime(
    ts_code: str,
    *,
    client_factory: Callable[[], DailyClient],
) -> dict[str, Any]:
    ts_code = _require_code(ts_code, "ts_code")
    return await client_factory().realtime(ts_code)


async def get_rt_min(
    ts_code: str,
    freq: str = "1MIN",
    limit: int = 1000,
    *,
    client_factory: Callable[[], DailyClient],
) -> list[dict[str, Any]]:
    ts_code = _require_code(ts_code, "ts_code")
    freq = _require_choice(freq, "freq", RT_MIN_FREQS)
    limit = _require_between(limit, "limit", 1, 1000)
    return await client_factory().rt_min(ts_code, freq, limit)


async def get_daily(
    ts_code: str,
    bars: int = 120,
    *,
    client_factory: Callable[[], DailyClient],
) -> list[dict[str, Any]]:
    ts_code = _require_code(ts_code, "ts_code")
    bars = _require_positive(bars, "bars")
    return await client_factory().daily_bars(ts_code, bars)


async def get_index_realtime(
    index_code: str,
    *,
    client_factory: Callable[[], DailyClient],
) -> dict[str, Any]:
    index_code = _require_code(index_code, "index_code")
    return await client_factory().index_realtime(index_code)


async def get_index_daily(
    index_code: str,
    bars: int = 60,
    *,
    client_factory: Callable[[], DailyClient],
) -> list[dict[str, Any]]:
    index_code = _require_code(index_code, "index_code")
    bars = _require_positive(bars, "bars")
    return await client_factory().index_daily_bars(index_code, bars)


async def get_moneyflow(
    ts_code: str,
    days: int = 10,
    *,
    client_factory: Callable[[], DailyClient],
) -> list[dict[str, Any]]:
    ts_code = _require_code(ts_code, "ts_code")
    days = _require_positive(days, "days")
    return await client_factory().moneyflow(ts_code, days)


async def get_hsgt_flow(
    days: int = 10,
    *,
    client_factory: Callable[[], DailyClient],
) -> list[dict[str, Any]]:
    days = _require_positive(days, "days")
    return await client_factory().hsgt_flow(days)


async def get_fina_indicator(
    ts_code: str,
    quarters: int = 8,
    *,
    client_factory: Callable[[], DailyClient],
) -> list[dict[str, Any]]:
    ts_code = _require_code(ts_code, "ts_code")
    quarters = _require_positive(quarters, "quarters")
    return await client_factory().fina_indicator(ts_code, quarters)


async def get_income(
    ts_code: str,
    quarters: int = 8,
    *,
    client_factory: Callable[[], DailyClient],
) -> list[dict[str, Any]]:
    ts_code = _require_code(ts_code, "ts_code")
    quarters = _require_positive(quarters, "quarters")
    return await client_factory().income(ts_code, quarters)


async def get_stock_basic(
    ts_code: str,
    *,
    client_factory: Callable[[], DailyClient],
) -> dict[str, Any]:
    ts_code = _require_code(ts_code, "ts_code")
    return await client_factory().stock_basic(ts_code)


GET_REALTIME_IMPL = get_realtime
GET_RT_MIN_IMPL = get_rt_min
GET_DAILY_IMPL = get_daily
GET_INDEX_REALTIME_IMPL = get_index_realtime
GET_INDEX_DAILY_IMPL = get_index_daily
GET_MONEYFLOW_IMPL = get_moneyflow
GET_HSGT_FLOW_IMPL = get_hsgt_flow
GET_FINA_INDICATOR_IMPL = get_fina_indicator
GET_INCOME_IMPL = get_income
GET_STOCK_BASIC_IMPL = get_stock_basic

RT_MIN_FREQS = {"1MIN", "5MIN", "15MIN", "30MIN", "60MIN"}


def register_tools(
    mcp: FastMCP,
    *,
    settings: Settings,
    client_factory: Callable[[], DailyClient],
) -> None:
    @mcp.tool()
    def health() -> dict[str, Any]:
        """Check whether the local Tushare MCP service is alive."""
        return health_check(settings)

    @mcp.tool()
    async def get_realtime(ts_code: str) -> dict[str, Any]:
        """Fetch realtime quote for a stock."""
        return await GET_REALTIME_IMPL(
            ts_code,
            client_factory=client_factory,
        )

    @mcp.tool()
    async def get_rt_min(
        ts_code: str,
        freq: str = "1MIN",
        limit: int = 1000,
    ) -> list[dict[str, Any]]:
        """Fetch realtime minute bars for A-share stocks, from 1min to 60min."""
        return await GET_RT_MIN_IMPL(
            ts_code,
            freq,
            limit,
            client_factory=client_factory,
        )

    @mcp.tool()
    async def get_daily(ts_code: str, bars: int = 120) -> list[dict[str, Any]]:
        """Fetch recent daily bars for a stock."""
        return await GET_DAILY_IMPL(
            ts_code,
            bars,
            client_factory=client_factory,
        )

    @mcp.tool()
    async def get_index_realtime(index_code: str) -> dict[str, Any]:
        """Fetch realtime quote for an index."""
        return await GET_INDEX_REALTIME_IMPL(
            index_code,
            client_factory=client_factory,
        )

    @mcp.tool()
    async def get_index_daily(
        index_code: str,
        bars: int = 60,
    ) -> list[dict[str, Any]]:
        """Fetch recent daily bars for an index."""
        return await GET_INDEX_DAILY_IMPL(
            index_code,
            bars,
            client_factory=client_factory,
        )

    @mcp.tool()
    async def get_moneyflow(
        ts_code: str,
        days: int = 10,
    ) -> list[dict[str, Any]]:
        """Fetch recent stock moneyflow records."""
        return await GET_MONEYFLOW_IMPL(
            ts_code,
            days,
            client_factory=client_factory,
        )

    @mcp.tool()
    async def get_hsgt_flow(days: int = 10) -> list[dict[str, Any]]:
        """Fetch recent northbound/southbound Stock Connect moneyflow records."""
        return await GET_HSGT_FLOW_IMPL(
            days,
            client_factory=client_factory,
        )

    @mcp.tool()
    async def get_fina_indicator(
        ts_code: str,
        quarters: int = 8,
    ) -> list[dict[str, Any]]:
        """Fetch recent financial indicator records."""
        return await GET_FINA_INDICATOR_IMPL(
            ts_code,
            quarters,
            client_factory=client_factory,
        )

    @mcp.tool()
    async def get_income(
        ts_code: str,
        quarters: int = 8,
    ) -> list[dict[str, Any]]:
        """Fetch recent income statement records."""
        return await GET_INCOME_IMPL(
            ts_code,
            quarters,
            client_factory=client_factory,
        )

    @mcp.tool()
    async def get_stock_basic(ts_code: str) -> dict[str, Any]:
        """Fetch basic stock metadata."""
        return await GET_STOCK_BASIC_IMPL(
            ts_code,
            client_factory=client_factory,
        )

    @mcp.tool()
    async def get_stock_daily(
        ts_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch daily stock market data from Tushare by ts_code."""
        return await stock_daily(
            ts_code,
            start_date,
            end_date,
            client_factory=client_factory,
        )
