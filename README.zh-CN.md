# tushare-local-mcp

[English](README.md)

一个本地运行的 MCP 服务，用来把 [Tushare](https://tushare.pro/) 的行情、资金和财务数据暴露给 MCP 客户端。

服务默认使用 Streamable HTTP，适合多个本地或服务器上的 MCP 客户端共享同一个 Tushare 数据服务。

## 功能

- 基于 Python 和 FastMCP 构建
- 默认 MCP endpoint：`http://127.0.0.1:8000/mcp`
- 支持 `.env` 和环境变量配置
- 提供股票实时行情、日线、指数日线、资金流、财务指标、利润表、股票基础信息等工具
- Tushare 适配层可测试，单元测试不需要真实 token
- 支持 Docker Compose 部署到服务器

## 环境要求

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- 调用真实 Tushare 数据时需要 Tushare token

## 本地快速启动

```bash
uv sync --dev
cp .env.example .env
```

编辑 `.env`，填入你的 Tushare token：

```bash
TUSHARE_TOKEN="你的 tushare token"
```

启动服务：

```bash
uv run tushare-local-mcp
```

默认 MCP endpoint：

```text
http://127.0.0.1:8000/mcp
```

## Docker 部署

适合部署到服务器长期运行：

```bash
cp .env.example .env
# 编辑 .env 并设置 TUSHARE_TOKEN
docker compose up -d --build
```

容器内服务会绑定到 `0.0.0.0:8000`，其他机器可以通过下面的地址访问：

```text
http://服务器IP:8000/mcp
```

更多部署、日志、更新和安全说明见 [docs/deploy.md](docs/deploy.md)。

## 验证 MCP 服务

保持服务运行，另开一个终端执行：

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

直接用浏览器打开 `/mcp` 不是合法的 MCP 请求。请使用 MCP 客户端，或使用上面的验证脚本。

## 配置

配置会从 `.env` 读取，也可以被环境变量覆盖。

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `TUSHARE_TOKEN` | 空 | Tushare API token |
| `TUSHARE_MCP_NAME` | `tushare-local-mcp` | MCP 服务名称 |
| `TUSHARE_MCP_TRANSPORT` | `streamable-http` | MCP 传输方式 |
| `TUSHARE_MCP_HOST` | `127.0.0.1` | HTTP 绑定地址 |
| `TUSHARE_MCP_PORT` | `8000` | HTTP 端口 |

如果要临时尝试 stdio：

```bash
TUSHARE_MCP_TRANSPORT=stdio uv run tushare-local-mcp
```

## 工具列表

### 健康检查

- `health() -> dict`

### 行情类

- `get_realtime(ts_code: str) -> dict`
- `get_rt_min(ts_code: str, freq: int = 1, limit: int = 1000) -> list[dict]`
- `get_daily(ts_code: str, bars: int = 120) -> list[dict]`
- `get_index_realtime(index_code: str) -> dict`
- `get_index_daily(index_code: str, bars: int = 60) -> list[dict]`

`get_rt_min` 用于获取 A 股实时分钟数据，`freq` 支持 `1` 到 `60` 分钟，
`limit` 单次最多 `1000` 行。`ts_code` 支持逗号分隔的多个股票代码。

### 资金类

- `get_moneyflow(ts_code: str, days: int = 10) -> list[dict]`
- `get_hsgt_flow(days: int = 10) -> list[dict]`

### 财务类

- `get_fina_indicator(ts_code: str, quarters: int = 8) -> list[dict]`
- `get_income(ts_code: str, quarters: int = 8) -> list[dict]`

### 基础信息

- `get_stock_basic(ts_code: str) -> dict`

### 兼容工具

- `get_stock_daily(ts_code: str, start_date: str | None = None, end_date: str | None = None) -> dict`

## 开发

```bash
uv run ruff check .
uv run pytest -q
```

## 项目结构

```text
src/tushare_local_mcp/
  config.py          环境变量和 .env 配置
  server.py          FastMCP app 工厂和启动入口
  tools.py           MCP 工具函数和注册逻辑
  tushare_client.py  Tushare SDK 适配层
tests/               配置、工具、服务注册和适配层映射测试
```

## 安全

不要提交 `.env` 或硬编码 token。公开仓库只保留 `.env.example`，真实凭据只放在本地或服务器上。

## 许可证

MIT
