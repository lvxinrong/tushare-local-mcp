from __future__ import annotations

import asyncio
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
        return await asyncio.to_thread(self._daily_sync, ts_code, start_date, end_date)

    async def realtime(self, ts_code: str) -> dict[str, Any]:
        return await asyncio.to_thread(self._realtime_sync, ts_code)

    async def daily_bars(self, ts_code: str, bars: int) -> list[dict[str, Any]]:
        return await asyncio.to_thread(self._pro_bar_sync, ts_code, bars, "E")

    async def index_daily_bars(
        self,
        index_code: str,
        bars: int,
    ) -> list[dict[str, Any]]:
        return await asyncio.to_thread(self._pro_bar_sync, index_code, bars, "I")

    async def moneyflow(self, ts_code: str, days: int) -> list[dict[str, Any]]:
        return await asyncio.to_thread(
            self._query_sync,
            "moneyflow",
            {"ts_code": ts_code, "limit": days},
        )

    async def hsgt_flow(self, days: int) -> list[dict[str, Any]]:
        return await asyncio.to_thread(
            self._query_sync,
            "moneyflow_hsgt",
            {"limit": days},
        )

    async def fina_indicator(
        self,
        ts_code: str,
        quarters: int,
    ) -> list[dict[str, Any]]:
        return await asyncio.to_thread(
            self._query_sync,
            "fina_indicator",
            {"ts_code": ts_code, "limit": quarters},
        )

    async def income(self, ts_code: str, quarters: int) -> list[dict[str, Any]]:
        return await asyncio.to_thread(
            self._query_sync,
            "income",
            {"ts_code": ts_code, "limit": quarters},
        )

    async def stock_basic(self, ts_code: str) -> dict[str, Any]:
        rows = await asyncio.to_thread(
            self._query_sync,
            "stock_basic",
            {"ts_code": ts_code, "limit": 1},
        )
        return rows[0] if rows else {}

    def _daily_sync(
        self,
        ts_code: str,
        start_date: str | None,
        end_date: str | None,
    ) -> list[dict[str, Any]]:
        if not self._token:
            raise RuntimeError("TUSHARE_TOKEN is required to query Tushare data.")

        import tushare as ts

        pro = ts.pro_api(self._token)
        data_frame = pro.daily(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date,
        )
        return self._records(data_frame)

    def _realtime_sync(self, ts_code: str) -> dict[str, Any]:
        import tushare as ts

        if hasattr(ts, "realtime_quote"):
            data_frame = ts.realtime_quote(ts_code=ts_code)
        else:
            data_frame = ts.get_realtime_quotes(ts_code)

        rows = self._records(data_frame)
        return rows[0] if rows else {}

    def _pro_bar_sync(
        self,
        ts_code: str,
        limit: int,
        asset: str,
    ) -> list[dict[str, Any]]:
        self._require_token()

        import tushare as ts

        pro = ts.pro_api(self._token)
        data_frame = ts.pro_bar(
            ts_code=ts_code,
            api=pro,
            asset=asset,
            limit=limit,
        )
        return self._records(data_frame)

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

    def _require_token(self) -> None:
        if not self._token:
            raise RuntimeError("TUSHARE_TOKEN is required to query Tushare data.")

    @staticmethod
    def _records(data_frame: Any) -> list[dict[str, Any]]:
        if data_frame is None:
            return []
        return data_frame.to_dict(orient="records")
