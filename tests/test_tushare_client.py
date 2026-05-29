import pandas as pd
import pytest
import tushare as ts

from tushare_local_mcp.tushare_client import TushareClient


@pytest.mark.asyncio
async def test_daily_bars_uses_pro_bar_for_stock(monkeypatch):
    calls = []
    fake_api = object()

    monkeypatch.setattr(ts, "pro_api", lambda token: fake_api)

    def fake_pro_bar(**kwargs):
        calls.append(kwargs)
        return pd.DataFrame([{"ts_code": kwargs["ts_code"], "asset": kwargs["asset"]}])

    monkeypatch.setattr(ts, "pro_bar", fake_pro_bar)

    rows = await TushareClient("secret-token").daily_bars("000001.SZ", 120)

    assert rows == [{"ts_code": "000001.SZ", "asset": "E"}]
    assert calls == [
        {
            "ts_code": "000001.SZ",
            "api": fake_api,
            "asset": "E",
            "limit": 120,
        }
    ]


@pytest.mark.asyncio
async def test_index_daily_bars_uses_pro_bar_for_index(monkeypatch):
    calls = []
    fake_api = object()

    monkeypatch.setattr(ts, "pro_api", lambda token: fake_api)
    monkeypatch.setattr(
        ts,
        "pro_bar",
        lambda **kwargs: calls.append(kwargs)
        or pd.DataFrame([{"ts_code": kwargs["ts_code"], "asset": kwargs["asset"]}]),
    )

    rows = await TushareClient("secret-token").index_daily_bars("000001.SH", 60)

    assert rows == [{"ts_code": "000001.SH", "asset": "I"}]
    assert calls[0]["asset"] == "I"
    assert calls[0]["limit"] == 60


@pytest.mark.asyncio
async def test_pro_query_methods_use_expected_api_names(monkeypatch):
    calls = []

    class FakePro:
        def query(self, api_name, **params):
            calls.append((api_name, params))
            return pd.DataFrame([{"api_name": api_name, **params}])

    monkeypatch.setattr(ts, "pro_api", lambda token: FakePro())

    client = TushareClient("secret-token")

    assert await client.moneyflow("000001.SZ", 10) == [
        {"api_name": "moneyflow", "ts_code": "000001.SZ", "limit": 10}
    ]
    assert await client.rt_min("000001.SZ,600000.SH", 5, 120) == [
        {
            "api_name": "rt_min",
            "ts_code": "000001.SZ,600000.SH",
            "freq": 5,
            "limit": 120,
        }
    ]
    assert await client.hsgt_flow(10) == [
        {"api_name": "moneyflow_hsgt", "limit": 10}
    ]
    assert await client.fina_indicator("000001.SZ", 8) == [
        {"api_name": "fina_indicator", "ts_code": "000001.SZ", "limit": 8}
    ]
    assert await client.income("000001.SZ", 8) == [
        {"api_name": "income", "ts_code": "000001.SZ", "limit": 8}
    ]
    assert await client.stock_basic("000001.SZ") == {
        "api_name": "stock_basic",
        "ts_code": "000001.SZ",
        "limit": 1,
    }

    assert calls == [
        ("moneyflow", {"ts_code": "000001.SZ", "limit": 10}),
        ("rt_min", {"ts_code": "000001.SZ,600000.SH", "freq": 5, "limit": 120}),
        ("moneyflow_hsgt", {"limit": 10}),
        ("fina_indicator", {"ts_code": "000001.SZ", "limit": 8}),
        ("income", {"ts_code": "000001.SZ", "limit": 8}),
        ("stock_basic", {"ts_code": "000001.SZ", "limit": 1}),
    ]


@pytest.mark.asyncio
async def test_realtime_uses_realtime_quote(monkeypatch):
    calls = []

    def fake_realtime_quote(**kwargs):
        calls.append(kwargs)
        return pd.DataFrame([{"ts_code": kwargs["ts_code"], "price": 12.3}])

    monkeypatch.setattr(ts, "realtime_quote", fake_realtime_quote)

    result = await TushareClient("secret-token").realtime("000001.SZ")

    assert result == {"ts_code": "000001.SZ", "price": 12.3}
    assert calls == [{"ts_code": "000001.SZ"}]
