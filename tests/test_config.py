from tushare_local_mcp.config import Settings


def test_settings_loads_http_defaults(monkeypatch, tmp_path):
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)
    monkeypatch.chdir(tmp_path)

    settings = Settings.from_env()

    assert settings.name == "tushare-local-mcp"
    assert settings.transport == "streamable-http"
    assert settings.host == "127.0.0.1"
    assert settings.port == 8000
    assert settings.tushare_token is None


def test_settings_reads_environment(monkeypatch):
    monkeypatch.setenv("TUSHARE_MCP_NAME", "local-tushare")
    monkeypatch.setenv("TUSHARE_MCP_TRANSPORT", "stdio")
    monkeypatch.setenv("TUSHARE_MCP_HOST", "0.0.0.0")
    monkeypatch.setenv("TUSHARE_MCP_PORT", "8123")
    monkeypatch.setenv("TUSHARE_TOKEN", "secret-token")

    settings = Settings.from_env()

    assert settings.name == "local-tushare"
    assert settings.transport == "stdio"
    assert settings.host == "0.0.0.0"
    assert settings.port == 8123
    assert settings.tushare_token == "secret-token"


def test_settings_loads_dotenv_file(monkeypatch, tmp_path):
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)
    monkeypatch.chdir(tmp_path)
    tmp_path.joinpath(".env").write_text(
        "TUSHARE_TOKEN=dotenv-token\n",
        encoding="utf-8",
    )

    settings = Settings.from_env()

    assert settings.tushare_token == "dotenv-token"
