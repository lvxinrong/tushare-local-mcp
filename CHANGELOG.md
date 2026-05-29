# Changelog

## 0.2.0

- Normalize MCP tool return shapes for analysis module compatibility.
- Convert realtime, daily, moneyflow, HSGT, financial, income, and stock basic
  responses to compact analysis-ready fields.
- Change `get_rt_min` `freq` to string values such as `"1MIN"` and `"5MIN"`.
- Change `get_stock_daily` to return a plain list of daily rows.
- Return empty `{}` or `[]` from the Tushare adapter when API calls fail.

## 0.1.0

- Add local Streamable HTTP MCP server scaffold.
- Add Tushare tools for market data, moneyflow, financial reports, and stock
  basics.
- Add `.env` support for local token configuration.
