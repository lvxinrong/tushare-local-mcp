import pandas as pd
import pytest
import tushare as ts

from tushare_local_mcp.config import Settings
from tushare_local_mcp.server import create_mcp
from tushare_local_mcp.tools import BOARD_TOOL_NAMES, query_board_tool
from tushare_local_mcp.tushare_client import TushareClient


def test_board_tool_names_cover_tushare_board_topic():
    assert BOARD_TOOL_NAMES == (
        "top_list",
        "top_inst",
        "limit_list_ths",
        "limit_list_d",
        "limit_step",
        "limit_cpt_list",
        "ths_index",
        "ths_daily",
        "ths_member",
        "dc_index",
        "dc_member",
        "dc_daily",
        "stking",
        "hm_list",
        "hm_detail",
        "hot_list",
        "dc_hot",
        "tdx_index",
        "tdx_member",
        "tdx_daily",
        "kpl_list",
        "kpl_concept_cons",
        "dc_theme",
        "dc_theme_cons",
    )


@pytest.mark.asyncio
async def test_create_mcp_registers_board_topic_tools():
    mcp = create_mcp(Settings())

    tool_names = {tool.name for tool in await mcp.list_tools()}

    assert set(BOARD_TOOL_NAMES).issubset(tool_names)


@pytest.mark.asyncio
async def test_query_board_tool_delegates_to_client_factory():
    class FakeClient:
        async def query_api(self, api_name, params):
            return [{"api_name": api_name, **params}]

    result = await query_board_tool(
        "limit_list_d",
        {"trade_date": "20260529", "limit_type": "U", "ignored": None},
        client_factory=lambda: FakeClient(),
    )

    assert result == [
        {
            "api_name": "limit_list_d",
            "trade_date": "20260529",
            "limit_type": "U",
        }
    ]


@pytest.mark.asyncio
async def test_query_board_tool_rejects_unknown_api():
    class FakeClient:
        async def query_api(self, api_name, params):
            return []

    with pytest.raises(ValueError, match="Unsupported board tool"):
        await query_board_tool(
            "not_a_tushare_api",
            {},
            client_factory=lambda: FakeClient(),
        )


@pytest.mark.asyncio
async def test_tushare_client_query_api_filters_none_params(monkeypatch):
    calls = []

    class FakePro:
        def query(self, api_name, **params):
            calls.append((api_name, params))
            return pd.DataFrame([{"api_name": api_name, **params}])

    monkeypatch.setattr(ts, "pro_api", lambda token: FakePro())

    result = await TushareClient("secret-token").query_api(
        "top_list",
        {"trade_date": "20260529", "ts_code": None},
    )

    assert result == [{"api_name": "top_list", "trade_date": "20260529"}]
    assert calls == [("top_list", {"trade_date": "20260529"})]
