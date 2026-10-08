from denue_explorer import settings


def test_fallback_without_prompt(monkeypatch):
    monkeypatch.delenv("INEGI_DENUE_TOKEN", raising=False)
    assert settings.load_token() == settings.BUILTIN_TOKEN
    assert settings.load_token()


def test_environment_override(monkeypatch):
    monkeypatch.setenv("INEGI_DENUE_TOKEN", "testing-token")
    assert settings.load_token() == "testing-token"


def test_empty_override_uses_default(monkeypatch):
    monkeypatch.setenv("INEGI_DENUE_TOKEN", "  ")
    assert settings.load_token() == settings.BUILTIN_TOKEN
