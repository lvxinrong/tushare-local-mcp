# tushare-local-mcp

[中文文档](README.zh-CN.md)

Local MCP server for exposing [Tushare](https://tushare.pro/) market and
financial data tools to MCP clients.

The server runs locally and uses Streamable HTTP by default, so multiple local
clients can share one Tushare-backed MCP service.

## Features

- Local-first MCP server built with Python and FastMCP
- Streamable HTTP endpoint at `http://127.0.0.1:8000/mcp`
- `.env` and environment variable configuration
- Tools for stock quotes, daily bars, index bars, moneyflow, financial
  indicators, income statements, and stock metadata
- Testable Tushare adapter layer with no token required for unit tests

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- A Tushare token for real data calls

## Quick Start

```bash
uv sync --dev
cp .env.example .env
```

Edit `.env` and set your token:

```bash
TUSHARE_TOKEN="your tushare token"
```

Start the server:

```bash
uv run tushare-local-mcp
```

The default MCP endpoint is:

```text
http://127.0.0.1:8000/mcp
```

## LAN Access

For access from other devices on the same LAN, bind the server to all network
interfaces:

```bash
TUSHARE_MCP_HOST=0.0.0.0 uv run tushare-local-mcp
```

Or set it in `.env`:

```bash
TUSHARE_MCP_HOST=0.0.0.0
```

Then connect clients to:

```text
http://YOUR_LAN_IP:8000/mcp
```

Keep `127.0.0.1` if only the current machine should access the service. On
macOS or Linux servers, make sure the firewall allows inbound TCP traffic on
port `8000`.

## Docker Deployment

For a server deployment:

```bash
cp .env.example .env
# edit .env and set TUSHARE_TOKEN
docker compose up -d --build
```

The container binds to `0.0.0.0:8000`, so other machines can reach:

```text
http://SERVER_IP:8000/mcp
```

See [docs/deploy.md](docs/deploy.md) for logs, updates, shutdown, and security
notes.

## Verify the MCP Server

Keep the server running, then open another terminal:

```bash
uv run python - <<'PY'
import anyio
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    async with streamablehttp_client("http://127.0.0.1:8000/mcp") as (
        read,
        write,
        _,
    ):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("TOOLS:")
            for tool in tools.tools:
                print("-", tool.name)

            result = await session.call_tool("health", {})
            print("\nHEALTH:")
            print(result.content)


anyio.run(main)
PY
```

Opening `/mcp` directly in a browser is not a valid MCP request. Use an MCP
client or the verification script above.

## Configuration

Configuration is read from `.env` first and can be overridden by environment
variables.

| Variable | Default | Description |
| --- | --- | --- |
| `TUSHARE_TOKEN` | empty | Tushare API token |
| `TUSHARE_MCP_NAME` | `tushare-local-mcp` | MCP server name |
| `TUSHARE_MCP_TRANSPORT` | `streamable-http` | MCP transport |
| `TUSHARE_MCP_HOST` | `127.0.0.1` | HTTP bind host. Use `0.0.0.0` for LAN access |
| `TUSHARE_MCP_PORT` | `8000` | HTTP bind port |

For stdio experiments:

```bash
TUSHARE_MCP_TRANSPORT=stdio uv run tushare-local-mcp
```

## Tools

### Health

- `health() -> dict`

### Market Data

- `get_realtime(ts_code: str) -> dict`
- `get_rt_min(ts_code: str, freq: str = "1MIN", limit: int = 1000) -> list[dict]`
- `get_daily(ts_code: str, bars: int = 120) -> list[dict]`
- `get_index_realtime(index_code: str) -> dict`
- `get_index_daily(index_code: str, bars: int = 60) -> list[dict]`

`get_rt_min` fetches A-share realtime minute bars. `freq` supports `"1MIN"`,
`"5MIN"`, `"15MIN"`, `"30MIN"`, and `"60MIN"`. `limit` is capped at `1000`
rows per request. `ts_code` can contain multiple comma-separated stock codes.

### Moneyflow

- `get_moneyflow(ts_code: str, days: int = 10) -> list[dict]`
- `get_hsgt_flow(days: int = 10) -> list[dict]`

### Financials

- `get_fina_indicator(ts_code: str, quarters: int = 8) -> list[dict]`
- `get_income(ts_code: str, quarters: int = 8) -> list[dict]`

### Reference Data

- `get_stock_basic(ts_code: str) -> dict`

### Compatibility

- `get_stock_daily(ts_code: str, start_date: str | None = None, end_date: str | None = None) -> list[dict]`

## Development

```bash
uv run ruff check .
uv run pytest -q
```

## Project Structure

```text
src/tushare_local_mcp/
  config.py          environment and .env settings
  server.py          FastMCP app factory and entrypoint
  tools.py           MCP tool functions and registration
  tushare_client.py  Tushare SDK adapter
tests/               unit tests for config, tools, server, and adapter mapping
```

## Security

Never commit `.env` or hard-coded tokens. Use `.env.example` as the public
template and keep real credentials local.

## License

MIT
