from __future__ import annotations

from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from .config import Settings
from .tools import register_tools
from .tushare_client import TushareClient


def create_mcp(
    settings: Settings | None = None,
    client_factory: Callable[[], TushareClient] | None = None,
) -> FastMCP:
    settings = settings or Settings.from_env()
    client_factory = client_factory or (lambda: TushareClient(settings.tushare_token))

    mcp = FastMCP(settings.name, host=settings.host, port=settings.port)
    register_tools(mcp, settings=settings, client_factory=client_factory)
    return mcp


def main() -> None:
    settings = Settings.from_env()
    mcp = create_mcp(settings)
    mcp.run(transport=settings.transport)
