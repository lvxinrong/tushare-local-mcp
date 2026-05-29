from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    name: str = "tushare-local-mcp"
    transport: str = "streamable-http"
    host: str = "127.0.0.1"
    port: int = 8000
    tushare_token: str | None = None

    @classmethod
    def from_env(cls) -> Settings:
        load_dotenv(dotenv_path=".env")

        return cls(
            name=os.getenv("TUSHARE_MCP_NAME", cls.name),
            transport=os.getenv("TUSHARE_MCP_TRANSPORT", cls.transport),
            host=os.getenv("TUSHARE_MCP_HOST", cls.host),
            port=int(os.getenv("TUSHARE_MCP_PORT", str(cls.port))),
            tushare_token=os.getenv("TUSHARE_TOKEN") or None,
        )
