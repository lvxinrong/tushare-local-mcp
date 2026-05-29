# Docker Deployment

This guide runs `tushare-local-mcp` as a long-lived Streamable HTTP service.

## Prerequisites

- Docker Engine
- Docker Compose
- A Tushare token

## Deploy

```bash
git clone git@github.com:lvxinrong/tushare-local-mcp.git
cd tushare-local-mcp
cp .env.example .env
```

Edit `.env`:

```bash
TUSHARE_TOKEN="your tushare token"
```

Start the service:

```bash
docker compose up -d --build
```

Check logs:

```bash
docker compose logs -f tushare-local-mcp
```

The MCP endpoint is:

```text
http://SERVER_IP:8000/mcp
```

## Verify

From a machine that can reach the server:

```bash
uv run python - <<'PY'
import anyio
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    async with streamablehttp_client("http://SERVER_IP:8000/mcp") as (
        read,
        write,
        _,
    ):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print([tool.name for tool in tools.tools])
            result = await session.call_tool("health", {})
            print(result.content)


anyio.run(main)
PY
```

Replace `SERVER_IP` with your server address.

## Update

```bash
git pull
docker compose up -d --build
```

## Stop

```bash
docker compose down
```

## Security Notes

- Do not expose port `8000` to the public internet unless you have a trusted
  network boundary, reverse proxy, or access control in front of it.
- Keep `.env` on the server only.
- Rotate `TUSHARE_TOKEN` if it is ever exposed.
- `docker compose config` expands `env_file` values and may print secrets.
