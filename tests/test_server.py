import pytest

from tushare_local_mcp.config import Settings
from tushare_local_mcp.server import create_mcp


def test_create_mcp_returns_named_server():
    mcp = create_mcp(Settings(name="local-tushare"))

    assert mcp.name == "local-tushare"


@pytest.mark.asyncio
async def test_create_mcp_registers_tushare_tools():
    mcp = create_mcp(Settings())

    tool_names = {tool.name for tool in await mcp.list_tools()}

    assert {
        "health",
        "get_realtime",
        "get_rt_min",
        "get_daily",
        "get_index_realtime",
        "get_index_daily",
        "get_moneyflow",
        "get_hsgt_flow",
        "get_fina_indicator",
        "get_income",
        "get_stock_basic",
        "get_stock_daily",
    }.issubset(tool_names)
