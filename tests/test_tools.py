import pytest

from tushare_local_mcp.config import Settings
from tushare_local_mcp.tools import (
    get_daily,
    get_fina_indicator,
    get_hsgt_flow,
    get_income,
    get_index_daily,
    get_index_realtime,
    get_moneyflow,
    get_realtime,
    get_rt_min,
    get_stock_basic,
    health_check,
    stock_daily,
)


def test_health_check_reports_configuration_state():
    settings = Settings(tushare_token="secret-token")

    result = health_check(settings)

    assert result == {
        "status": "ok",
        "service": "tushare-local-mcp",
        "transport": "streamable-http",
        "tushare_token_configured": True,
    }


@pytest.mark.asyncio
async def test_stock_daily_delegates_to_client_factory():
    class FakeClient:
        async def daily(self, ts_code, start_date, end_date):
            return [
                {
                    "ts_code": ts_code,
                    "trade_date": start_date,
                    "close": 10.5,
                }
            ]

    result = await stock_daily(
        "000001.SZ",
        "20240101",
        "20240131",
        client_factory=lambda: FakeClient(),
    )

    assert result == [
        {
            "ts_code": "000001.SZ",
            "trade_date": "20240101",
            "close": 10.5,
        }
    ]


@pytest.mark.asyncio
async def test_market_tools_delegate_to_client_methods():
    class FakeClient:
        async def realtime(self, ts_code):
            return {"ts_code": ts_code, "price": 12.3}

        async def rt_min(self, ts_code, freq, limit):
            return [{"ts_code": ts_code, "freq": freq, "limit": limit}]

        async def index_realtime(self, index_code):
            return {"ts_code": index_code, "price": 4037.95}

        async def daily_bars(self, ts_code, bars):
            return [{"ts_code": ts_code, "bars": bars}]

        async def index_daily_bars(self, index_code, bars):
            return [{"ts_code": index_code, "bars": bars}]

    fake = FakeClient()

    assert await get_realtime("000001.SZ", client_factory=lambda: fake) == {
        "ts_code": "000001.SZ",
        "price": 12.3,
    }
    assert await get_daily("000001.SZ", client_factory=lambda: fake) == [
        {"ts_code": "000001.SZ", "bars": 120}
    ]
    assert await get_index_realtime("000001.SH", client_factory=lambda: fake) == {
        "ts_code": "000001.SH",
        "price": 4037.95,
    }
    assert await get_index_daily("000001.SH", client_factory=lambda: fake) == [
        {"ts_code": "000001.SH", "bars": 60}
    ]
    assert await get_rt_min("000001.SZ", client_factory=lambda: fake) == [
        {"ts_code": "000001.SZ", "freq": "1MIN", "limit": 1000}
    ]


@pytest.mark.asyncio
async def test_rt_min_accepts_frequency_and_limit():
    class FakeClient:
        async def rt_min(self, ts_code, freq, limit):
            return [{"ts_code": ts_code, "freq": freq, "limit": limit}]

    result = await get_rt_min(
        "000001.SZ,600000.SH",
        freq="5MIN",
        limit=120,
        client_factory=lambda: FakeClient(),
    )

    assert result == [
        {"ts_code": "000001.SZ,600000.SH", "freq": "5MIN", "limit": 120}
    ]


@pytest.mark.asyncio
async def test_moneyflow_tools_delegate_to_client_methods():
    class FakeClient:
        async def moneyflow(self, ts_code, days):
            return [{"ts_code": ts_code, "days": days}]

        async def hsgt_flow(self, days):
            return [{"trade_date": "20240101", "days": days}]

    fake = FakeClient()

    assert await get_moneyflow("000001.SZ", client_factory=lambda: fake) == [
        {"ts_code": "000001.SZ", "days": 10}
    ]
    assert await get_hsgt_flow(client_factory=lambda: fake) == [
        {"trade_date": "20240101", "days": 10}
    ]


@pytest.mark.asyncio
async def test_financial_tools_delegate_to_client_methods():
    class FakeClient:
        async def fina_indicator(self, ts_code, quarters):
            return [{"ts_code": ts_code, "quarters": quarters}]

        async def income(self, ts_code, quarters):
            return [{"ts_code": ts_code, "quarters": quarters}]

    fake = FakeClient()

    assert await get_fina_indicator("000001.SZ", client_factory=lambda: fake) == [
        {"ts_code": "000001.SZ", "quarters": 8}
    ]
    assert await get_income("000001.SZ", client_factory=lambda: fake) == [
        {"ts_code": "000001.SZ", "quarters": 8}
    ]


@pytest.mark.asyncio
async def test_stock_basic_returns_single_record():
    class FakeClient:
        async def stock_basic(self, ts_code):
            return {"ts_code": ts_code, "name": "平安银行"}

    result = await get_stock_basic("000001.SZ", client_factory=lambda: FakeClient())

    assert result == {"ts_code": "000001.SZ", "name": "平安银行"}


@pytest.mark.asyncio
async def test_tool_functions_reject_blank_codes():
    class FakeClient:
        async def daily_bars(self, ts_code, bars):
            return []

    with pytest.raises(ValueError, match="ts_code must not be blank"):
        await get_daily("   ", client_factory=lambda: FakeClient())


@pytest.mark.asyncio
async def test_tool_functions_reject_non_positive_limits():
    class FakeClient:
        async def moneyflow(self, ts_code, days):
            return []

    with pytest.raises(ValueError, match="days must be greater than 0"):
        await get_moneyflow("000001.SZ", days=0, client_factory=lambda: FakeClient())


@pytest.mark.asyncio
async def test_rt_min_rejects_invalid_frequency_and_limit():
    class FakeClient:
        async def rt_min(self, ts_code, freq, limit):
            return []

    with pytest.raises(ValueError, match="freq must be one of"):
        await get_rt_min("000001.SZ", freq="2MIN", client_factory=lambda: FakeClient())

    with pytest.raises(ValueError, match="limit must be between 1 and 1000"):
        await get_rt_min("000001.SZ", limit=1001, client_factory=lambda: FakeClient())
