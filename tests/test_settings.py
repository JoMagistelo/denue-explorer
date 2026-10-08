from denue_explorer import settings


def test_fallback_without_prompt(monkeypatch):
    monkeypatch.delenv("INEGI_DENUE_TOKEN", raising=False)
    assert settings.load_token() == settings.BUILTIN_TOKEN
    assert settings.load_token()


def test_old_environment_does_not_override_code_token(monkeypatch):
    monkeypatch.setenv("INEGI_DENUE_TOKEN", "stale-token")
    assert settings.load_token() == settings.BUILTIN_TOKEN
    assert settings.token_source() == "settings.py (token incorporado)"

def test_env_fallback_without_code_token(monkeypatch):
    monkeypatch.setattr(settings, "BUILTIN_TOKEN", "")
    monkeypatch.setenv("INEGI_DENUE_TOKEN", "testing-token")
    assert settings.load_token() == "testing-token"
    assert settings.token_source() == "variable INEGI_DENUE_TOKEN"


def test_empty_override_uses_default(monkeypatch):
    monkeypatch.setenv("INEGI_DENUE_TOKEN", "  ")
    assert settings.load_token() == settings.BUILTIN_TOKEN

def test_no_token_when_both_sources_empty(monkeypatch):
    monkeypatch.setattr(settings, "BUILTIN_TOKEN", "")
    monkeypatch.delenv("INEGI_DENUE_TOKEN", raising=False)
    assert settings.load_token() == ""
    assert settings.token_source().startswith("ninguna")

def test_local_token_module_overrides_old_public_key(monkeypatch):
    """Al actualizar, la copia local del token debe prevalecer."""
    import sys
    import types
    private_settings = types.ModuleType("denue_explorer.local_token")
    private_settings.BUILTIN_TOKEN = "new-private-token-for-test"
    monkeypatch.setitem(sys.modules, "denue_explorer.local_token", private_settings)
    monkeypatch.setenv("INEGI_DENUE_TOKEN", "old-env-token")
    assert settings.load_token() == "new-private-token-for-test"
    assert settings.token_source() == "local_token.py (solo este equipo)"


def test_ignored_private_token_has_no_need_for_manual_setup(monkeypatch):
    """El programa usa automáticamente la copia local si existe."""
    import sys
    import types
    private_settings = types.ModuleType("denue_explorer.local_token")
    private_settings.BUILTIN_TOKEN = "some-local-value"
    monkeypatch.setitem(sys.modules, "denue_explorer.local_token", private_settings)
    assert settings.load_token() == "some-local-value"
