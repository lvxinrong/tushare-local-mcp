# Contributing

Thanks for helping improve `tushare-local-mcp`.

## Development Setup

```bash
uv sync --dev
cp .env.example .env
```

Put your own Tushare token in `.env` when you need to call real APIs.

## Verification

Run these before opening a pull request:

```bash
uv run ruff check .
uv run pytest -q
```

## Pull Requests

- Keep each pull request focused on one change.
- Add or update tests for MCP tools and Tushare API mappings.
- Do not commit `.env`, tokens, API responses with private data, or IDE state.
- Prefer small adapters around Tushare APIs instead of putting provider logic in
  MCP tool registration code.
