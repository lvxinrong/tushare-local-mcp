from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_runs_installed_mcp_entrypoint():
    dockerfile = ROOT.joinpath("Dockerfile").read_text(encoding="utf-8")

    assert "FROM python:3.12-slim" in dockerfile
    assert "uv sync --frozen --no-dev" in dockerfile
    assert 'CMD ["uv", "run", "tushare-local-mcp"]' in dockerfile


def test_compose_exposes_streamable_http_service():
    compose = ROOT.joinpath("docker-compose.yml").read_text(encoding="utf-8")

    assert "tushare-local-mcp:" in compose
    assert "8000:8000" in compose
    assert "TUSHARE_MCP_HOST: 0.0.0.0" in compose
    assert "TUSHARE_MCP_TRANSPORT: streamable-http" in compose
    assert "env_file:" in compose


def test_dockerignore_excludes_local_secrets_and_caches():
    dockerignore = ROOT.joinpath(".dockerignore").read_text(encoding="utf-8")

    assert ".env" in dockerignore
    assert ".venv" in dockerignore
    assert ".git" in dockerignore
