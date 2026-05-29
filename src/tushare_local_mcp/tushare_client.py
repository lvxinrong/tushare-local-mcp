from __future__ import annotations

import asyncio
import math
from collections.abc import Callable
from typing import Any


class TushareClient:
    def __init__(self, token: str | None) -> None:
        self._token = token

    async def daily(
        self,
        ts_code: str,
        start_date: str | None,
        end_date: str | None,
    ) -> list[dict[str, Any]]:
        return await self._safe_list(self._daily_sync, ts_code, start_date, end_date)

    async def realtime(self, ts_code: str) -> dict[str, Any]:
        return await self._safe_dict(self._realtime_sync, ts_code)

    async def index_realtime(self, index_code: str) -> dict[str, Any]:
        return await self._safe_dict(self._index_realtime_sync, index_code)

    async def rt_min(
        self,
        ts_code: str,
        freq: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        return await self._safe_list(
            self._query_sync,
            "rt_min",
            {"ts_code": ts_code, "freq": freq, "limit": limit},
        )

    async def daily_bars(self, ts_code: str, bars: int) -> list[dict[str, Any]]:
        return await self._safe_list(self._daily_bars_sync, ts_code, bars)

    async def index_daily_bars(
        self,
        index_code: str,
        bars: int,
    ) -> list[dict[str, Any]]:
        return await self._safe_list(self._index_daily_bars_sync, index_code, bars)

    async def moneyflow(self, ts_code: str, days: int) -> list[dict[str, Any]]:
        rows = await self._safe_list(
            self._query_sync,
            "moneyflow",
            {"ts_code": ts_code, "limit": days},
        )
        return [self._format_moneyflow(row) for row in rows]

    async def hsgt_flow(self, days: int) -> list[dict[str, Any]]:
        rows = await self._safe_list(
            self._query_sync,
            "moneyflow_hsgt",
            {"limit": days},
        )
        return [self._format_hsgt_flow(row) for row in rows]

    async def fina_indicator(
        self,
        ts_code: str,
        quarters: int,
    ) -> list[dict[str, Any]]:
        rows = await self._safe_list(
            self._query_sync,
            "fina_indicator",
            {"ts_code": ts_code, "limit": quarters},
        )
        return [self._pick(row, FINA_INDICATOR_FIELDS) for row in rows]

    async def income(self, ts_code: str, quarters: int) -> list[dict[str, Any]]:
        rows = await self._safe_list(
            self._query_sync,
            "income",
            {"ts_code": ts_code, "limit": quarters},
        )
        return [self._pick(row, INCOME_FIELDS) for row in rows]

    async def stock_basic(self, ts_code: str) -> dict[str, Any]:
        rows = await self._safe_list(
            self._query_sync,
            "stock_basic",
            {"ts_code": ts_code, "limit": 1},
        )
        return self._pick(rows[0], STOCK_BASIC_FIELDS) if rows else {}

    async def _safe_list(
        self,
        func: Callable[..., list[dict[str, Any]]],
        *args: Any,
    ) -> list[dict[str, Any]]:
        try:
            return await asyncio.to_thread(func, *args)
        except Exception:
            return []

    async def _safe_dict(
        self,
        func: Callable[..., dict[str, Any]],
        *args: Any,
    ) -> dict[str, Any]:
        try:
            return await asyncio.to_thread(func, *args)
        except Exception:
            return {}

    def _daily_sync(
        self,
        ts_code: str,
        start_date: str | None,
        end_date: str | None,
    ) -> list[dict[str, Any]]:
        self._require_token()

        import tushare as ts

        pro = ts.pro_api(self._token)
        data_frame = pro.daily(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date,
        )
        return [self._format_daily(row) for row in self._records(data_frame)]

    def _realtime_sync(self, ts_code: str) -> dict[str, Any]:
        self._require_token()

        import tushare as ts

        pro = ts.pro_api(self._token)
        rows: list[dict[str, Any]] = []

        if hasattr(pro, "rt_k"):
            rows = self._records(pro.rt_k(ts_code))

        if not rows and hasattr(pro, "daily"):
            rows = self._records(pro.daily(ts_code=ts_code, limit=1))

        if not rows:
            rows = self._tx_get_realtime(ts_code)

        if not rows:
            return {}

        daily_basic = self._first_record(pro.daily_basic(ts_code=ts_code, limit=1))
        return self._format_realtime(rows[0], daily_basic)

    def _index_realtime_sync(self, index_code: str) -> dict[str, Any]:
        self._require_token()

        import tushare as ts

        pro = ts.pro_api(self._token)
        rows: list[dict[str, Any]] = []

        if hasattr(pro, "rt_idx_k"):
            rows = self._records(pro.rt_idx_k(index_code))

        if not rows and hasattr(pro, "index_daily"):
            rows = self._records(pro.index_daily(ts_code=index_code, limit=1))

        return self._format_index_realtime(rows[0]) if rows else {}

    def _daily_bars_sync(self, ts_code: str, limit: int) -> list[dict[str, Any]]:
        self._require_token()

        import tushare as ts

        pro = ts.pro_api(self._token)
        data_frame = pro.daily(ts_code=ts_code, limit=limit)
        return [self._format_daily(row) for row in self._records(data_frame)]

    def _index_daily_bars_sync(
        self,
        index_code: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        self._require_token()

        import tushare as ts

        pro = ts.pro_api(self._token)
        data_frame = pro.index_daily(ts_code=index_code, limit=limit)
        return [self._format_index_daily(row) for row in self._records(data_frame)]

    def _query_sync(
        self,
        api_name: str,
        params: dict[str, Any],
    ) -> list[dict[str, Any]]:
        self._require_token()

        import tushare as ts

        pro = ts.pro_api(self._token)
        data_frame = pro.query(api_name, **params)
        return self._records(data_frame)

    def _tx_get_realtime(self, ts_code: str) -> list[dict[str, Any]]:
        import tushare as ts

        if not hasattr(ts, "realtime_quote"):
            return self._records(ts.get_realtime_quotes(ts_code))

        try:
            return self._records(ts.realtime_quote(ts_code=ts_code))
        except TypeError:
            return self._records(ts.realtime_quote(ts_code))

    @staticmethod
    def _format_realtime(
        row: dict[str, Any],
        daily_basic: dict[str, Any],
    ) -> dict[str, Any]:
        ts_code = _value(row, "ts_code", "TS_CODE", default="")
        price = _number(_value(row, "price", "PRICE"))
        prev_close = _number(_value(row, "pre_close", "PRE_CLOSE"))
        high = _number(_value(row, "high", "HIGH"))
        low = _number(_value(row, "low", "LOW"))

        return {
            "name": _value(row, "name", "NAME", default=""),
            "code": str(ts_code).split(".")[0],
            "price": price,
            "open": _number(_value(row, "open", "OPEN")),
            "high": high,
            "low": low,
            "volume": _number(_value(row, "volume", "VOLUME", "vol")),
            "amount": _round(_number(_value(row, "amount", "AMOUNT")) / 1e8, 2),
            "prev_close": prev_close,
            "chg_pct": _pct_change(price, prev_close),
            "pe": _number(_value(daily_basic, "pe")),
            "market_cap": _round(_number(_value(daily_basic, "total_mv")) / 1e4, 2),
            "turnover": _number(_value(daily_basic, "turnover_rate")),
            "amplitude": _pct_change(high, low),
        }

    @staticmethod
    def _format_index_realtime(row: dict[str, Any]) -> dict[str, Any]:
        price = _number(_value(row, "price", "PRICE", "close"))
        prev_close = _number(_value(row, "pre_close", "PRE_CLOSE"))
        pct = _value(row, "pct_chg", "PCT_CHG", "change_pct")

        return {
            "price": price,
            "chg_pct": (
                _number(pct) if pct is not None else _pct_change(price, prev_close)
            ),
            "high": _number(_value(row, "high", "HIGH")),
            "low": _number(_value(row, "low", "LOW")),
        }

    @staticmethod
    def _format_daily(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "date": _value(row, "trade_date", "date", default=""),
            "open": _number(_value(row, "open")),
            "close": _number(_value(row, "close")),
            "high": _number(_value(row, "high")),
            "low": _number(_value(row, "low")),
            "volume": _number(_value(row, "volume", "vol")),
            "amount": _number(_value(row, "amount")),
            "change_pct": _number(_value(row, "pct_chg", "change_pct")),
            "turnover": _number(_value(row, "turnover", "turnover_rate", default=0)),
        }

    @staticmethod
    def _format_index_daily(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "date": _value(row, "trade_date", "date", default=""),
            "open": _number(_value(row, "open")),
            "close": _number(_value(row, "close")),
            "high": _number(_value(row, "high")),
            "low": _number(_value(row, "low")),
            "volume": _number(_value(row, "volume", "vol")),
            "amount": _number(_value(row, "amount")),
        }

    @staticmethod
    def _format_moneyflow(row: dict[str, Any]) -> dict[str, Any]:
        buy_elg = _number(_value(row, "buy_elg_amount"))
        sell_elg = _number(_value(row, "sell_elg_amount"))
        buy_lg = _number(_value(row, "buy_lg_amount"))
        sell_lg = _number(_value(row, "sell_lg_amount"))
        buy_md = _number(_value(row, "buy_md_amount"))
        sell_md = _number(_value(row, "sell_md_amount"))
        buy_sm = _number(_value(row, "buy_sm_amount"))
        sell_sm = _number(_value(row, "sell_sm_amount"))

        return {
            "date": _value(row, "trade_date", "date", default=""),
            "main_net": _round((buy_elg + buy_lg - sell_elg - sell_lg) / 1e4, 2),
            "super_large_net": _round((buy_elg - sell_elg) / 1e4, 2),
            "large_net": _round((buy_lg - sell_lg) / 1e4, 2),
            "mid_net": _round((buy_md - sell_md) / 1e4, 2),
            "small_net": _round((buy_sm - sell_sm) / 1e4, 2),
            "main_pct": 0,
        }

    @staticmethod
    def _format_hsgt_flow(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "date": _value(row, "trade_date", "date", default=""),
            "ggt_ss": _round(_number(_value(row, "ggt_ss")) / 1e4, 2),
            "ggt_sz": _round(_number(_value(row, "ggt_sz")) / 1e4, 2),
            "north_money": _round(_number(_value(row, "north_money")) / 1e4, 2),
        }

    @staticmethod
    def _pick(row: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
        return {field: _value(row, field) for field in fields}

    def _require_token(self) -> None:
        if not self._token:
            raise RuntimeError("TUSHARE_TOKEN is required to query Tushare data.")

    @staticmethod
    def _first_record(data_frame: Any) -> dict[str, Any]:
        rows = TushareClient._records(data_frame)
        return rows[0] if rows else {}

    @staticmethod
    def _records(data_frame: Any) -> list[dict[str, Any]]:
        if data_frame is None:
            return []
        return data_frame.to_dict(orient="records")


FINA_INDICATOR_FIELDS = (
    "end_date",
    "roe",
    "grossprofit_margin",
    "netprofit_margin",
    "debt_to_assets",
    "current_ratio",
    "eps",
    "bps",
)
INCOME_FIELDS = ("end_date", "total_revenue", "revenue", "n_income")
STOCK_BASIC_FIELDS = ("ts_code", "name", "industry", "market", "list_date")


def _value(row: dict[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in row and not _is_missing(row[name]):
            return row[name]
        upper_name = name.upper()
        if upper_name in row and not _is_missing(row[upper_name]):
            return row[upper_name]
        lower_name = name.lower()
        if lower_name in row and not _is_missing(row[lower_name]):
            return row[lower_name]
    return default


def _number(value: Any) -> int | float:
    if _is_missing(value):
        return 0

    number = float(value)
    if number.is_integer():
        return int(number)
    return number


def _round(value: int | float, digits: int) -> int | float:
    rounded = round(float(value), digits)
    if rounded.is_integer():
        return int(rounded)
    return rounded


def _pct_change(value: int | float, base: int | float) -> int | float:
    if base == 0:
        return 0
    return _round((float(value) - float(base)) / float(base) * 100, 2)


def _is_missing(value: Any) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))
