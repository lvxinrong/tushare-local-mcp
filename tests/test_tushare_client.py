import pandas as pd
import pytest
import tushare as ts

from tushare_local_mcp.tushare_client import TushareClient


class FakePro:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def query(self, api_name, **params):
        self.calls.append((api_name, params))
        if api_name == "moneyflow":
            return pd.DataFrame(
                [
                    {
                        "trade_date": "20260529",
                        "buy_sm_amount": 304003.42,
                        "sell_sm_amount": 213386.46,
                        "buy_md_amount": 40000.0,
                        "sell_md_amount": 17000.0,
                        "buy_lg_amount": 501224.0,
                        "sell_lg_amount": 558224.0,
                        "buy_elg_amount": 449186.0,
                        "sell_elg_amount": 558224.0,
                    }
                ]
            )
        if api_name == "moneyflow_hsgt":
            return pd.DataFrame(
                [
                    {
                        "trade_date": "20260529",
                        "ggt_ss": 30000.0,
                        "ggt_sz": 23000.0,
                        "north_money": 1900000.0,
                    }
                ]
            )
        if api_name == "rt_min":
            return pd.DataFrame(
                [
                    {
                        "ts_code": params["ts_code"],
                        "freq": params["freq"],
                        "close": 10.5,
                    }
                ]
            )
        if api_name == "fina_indicator":
            return pd.DataFrame(
                [
                    {
                        "end_date": "20260331",
                        "roe": 4.8,
                        "grossprofit_margin": 33.3,
                        "netprofit_margin": 14.4,
                        "debt_to_assets": 57.5,
                        "current_ratio": 1.7,
                        "eps": 1.12,
                        "bps": 23.47,
                        "extra": "ignored",
                    }
                ]
            )
        if api_name == "income":
            return pd.DataFrame(
                [
                    {
                        "end_date": "20260331",
                        "total_revenue": 435.3,
                        "revenue": 435.3,
                        "n_income": 78.3,
                        "extra": "ignored",
                    }
                ]
            )
        if api_name == "stock_basic":
            return pd.DataFrame(
                [
                    {
                        "ts_code": "300274.SZ",
                        "name": "阳光电源",
                        "industry": "电气设备",
                        "market": "SZ",
                        "list_date": "20130423",
                        "extra": "ignored",
                    }
                ]
            )
        return pd.DataFrame()

    def rt_k(self, *, ts_code):
        return pd.DataFrame(
            [
                {
                    "NAME": "阳光电源",
                    "TS_CODE": ts_code,
                    "close": 177.99,
                    "PRE_CLOSE": 190.09,
                    "OPEN": 190.14,
                    "HIGH": 190.63,
                    "LOW": 176.0,
                    "VOLUME": 88135127,
                    "AMOUNT": 16012780210,
                }
            ]
        )

    def rt_idx_k(self, *, ts_code):
        return pd.DataFrame(
            [
                {
                    "TS_CODE": ts_code,
                    "PRICE": 4037.95,
                    "PRE_CLOSE": 4125.0,
                    "HIGH": 4158.69,
                    "LOW": 4010.12,
                }
            ]
        )

    def daily_basic(self, ts_code, limit=1):
        return pd.DataFrame(
            [
                {
                    "ts_code": ts_code,
                    "pe": 27.4,
                    "total_mv": 36900000.0,
                    "turnover_rate": 5.54,
                }
            ]
        )

    def daily(self, ts_code, start_date=None, end_date=None, offset=None, limit=None):
        return pd.DataFrame(
            [
                {
                    "ts_code": ts_code,
                    "trade_date": "20260529",
                    "open": 190.14,
                    "close": 177.99,
                    "high": 190.63,
                    "low": 176.0,
                    "vol": 88135127,
                    "amount": 16012780210,
                    "pct_chg": -6.3654,
                }
            ]
        )

    def index_daily(self, ts_code, limit=None, start_date=None, end_date=None):
        return pd.DataFrame(
            [
                {
                    "ts_code": ts_code,
                    "trade_date": "20260529",
                    "open": 4141.91,
                    "close": 4037.95,
                    "high": 4158.69,
                    "low": 4010.12,
                    "vol": 4379944000,
                    "amount": 354854100000,
                }
            ]
        )


@pytest.fixture
def fake_pro(monkeypatch):
    pro = FakePro()
    monkeypatch.setattr(ts, "pro_api", lambda token: pro)
    return pro


@pytest.mark.asyncio
async def test_realtime_returns_analysis_ready_quote(fake_pro):
    result = await TushareClient("secret-token").realtime("300274.SZ")

    assert result == {
        "name": "阳光电源",
        "code": "300274",
        "price": 177.99,
        "open": 190.14,
        "high": 190.63,
        "low": 176.0,
        "volume": 88135127,
        "amount": 160.13,
        "prev_close": 190.09,
        "chg_pct": -6.37,
        "pe": 27.4,
        "market_cap": 3690.0,
        "turnover": 5.54,
        "amplitude": 8.31,
    }


@pytest.mark.asyncio
async def test_index_realtime_returns_analysis_ready_quote(fake_pro):
    result = await TushareClient("secret-token").index_realtime("000001.SH")

    assert result == {
        "price": 4037.95,
        "chg_pct": -2.11,
        "high": 4158.69,
        "low": 4010.12,
    }


@pytest.mark.asyncio
async def test_index_realtime_falls_back_to_index_daily(monkeypatch):
    class FallbackPro(FakePro):
        def rt_idx_k(self, *, ts_code):
            raise RuntimeError("frequency limited")

    pro = FallbackPro()
    monkeypatch.setattr(ts, "pro_api", lambda token: pro)

    result = await TushareClient("secret-token").index_realtime("000001.SH")

    assert result == {
        "price": 4037.95,
        "chg_pct": 0,
        "high": 4158.69,
        "low": 4010.12,
    }


@pytest.mark.asyncio
async def test_daily_bars_returns_analysis_ready_rows(fake_pro):
    rows = await TushareClient("secret-token").daily_bars("300274.SZ", 120)

    assert rows == [
        {
            "date": "20260529",
            "open": 190.14,
            "close": 177.99,
            "high": 190.63,
            "low": 176.0,
            "volume": 88135127,
            "amount": 16012780210,
            "change_pct": -6.3654,
            "turnover": 0,
        }
    ]


@pytest.mark.asyncio
async def test_index_daily_bars_returns_analysis_ready_rows(fake_pro):
    rows = await TushareClient("secret-token").index_daily_bars("000001.SH", 60)

    assert rows == [
        {
            "date": "20260529",
            "open": 4141.91,
            "close": 4037.95,
            "high": 4158.69,
            "low": 4010.12,
            "volume": 4379944000,
            "amount": 354854100000,
        }
    ]


@pytest.mark.asyncio
async def test_moneyflow_returns_net_amounts_in_yi(fake_pro):
    rows = await TushareClient("secret-token").moneyflow("300274.SZ", 10)

    assert rows == [
        {
            "date": "20260529",
            "main_net": -16.6,
            "super_large_net": -10.9,
            "large_net": -5.7,
            "mid_net": 2.3,
            "small_net": 9.06,
            "main_pct": 0,
        }
    ]


@pytest.mark.asyncio
async def test_hsgt_flow_returns_analysis_ready_rows(fake_pro):
    rows = await TushareClient("secret-token").hsgt_flow(10)

    assert rows == [
        {
            "date": "20260529",
            "ggt_ss": 3.0,
            "ggt_sz": 2.3,
            "north_money": 190.0,
        }
    ]
    api_name, params = fake_pro.calls[-1]
    assert api_name == "moneyflow_hsgt"
    assert "start_date" in params
    assert "end_date" in params
    assert "limit" not in params


@pytest.mark.asyncio
async def test_financial_reports_keep_only_core_fields(fake_pro):
    client = TushareClient("secret-token")

    assert await client.fina_indicator("300274.SZ", 8) == [
        {
            "end_date": "20260331",
            "roe": 4.8,
            "grossprofit_margin": 33.3,
            "netprofit_margin": 14.4,
            "debt_to_assets": 57.5,
            "current_ratio": 1.7,
            "eps": 1.12,
            "bps": 23.47,
        }
    ]
    assert await client.income("300274.SZ", 8) == [
        {
            "end_date": "20260331",
            "total_revenue": 435.3,
            "revenue": 435.3,
            "n_income": 78.3,
        }
    ]


@pytest.mark.asyncio
async def test_stock_basic_keeps_only_core_fields(fake_pro):
    result = await TushareClient("secret-token").stock_basic("300274.SZ")

    assert result == {
        "ts_code": "300274.SZ",
        "name": "阳光电源",
        "industry": "电气设备",
        "market": "SZ",
        "list_date": "20130423",
    }


@pytest.mark.asyncio
async def test_rt_min_uses_string_frequency(fake_pro):
    rows = await TushareClient("secret-token").rt_min(
        "000001.SZ,600000.SH",
        "5MIN",
        120,
    )

    assert rows == [
        {
            "ts_code": "000001.SZ,600000.SH",
            "freq": "5MIN",
            "close": 10.5,
        }
    ]
    assert (
        "rt_min",
        {"ts_code": "000001.SZ,600000.SH", "freq": "5MIN", "limit": 120},
    ) in fake_pro.calls


@pytest.mark.asyncio
async def test_api_failures_return_empty_results(monkeypatch):
    class FailingPro:
        def query(self, api_name, **params):
            raise RuntimeError("boom")

    monkeypatch.setattr(ts, "pro_api", lambda token: FailingPro())

    client = TushareClient("secret-token")

    assert await client.moneyflow("300274.SZ", 10) == []
    assert await client.stock_basic("300274.SZ") == {}
