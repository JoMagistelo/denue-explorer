from denue_explorer import diagnostics, settings
from denue_explorer.client import DenueError


def test_diagnostic_uses_loaded_token_without_printing_it(monkeypatch, capsys):
    secret = "example-token-not-for-output"
    monkeypatch.setattr(settings, "BUILTIN_TOKEN", secret)
    monkeypatch.delenv("INEGI_DENUE_TOKEN", raising=False)
    seen = {}
    def fake_search(query, token, **kwargs):
        seen["token"] = token
        return [{"Id": "1"}]
    monkeypatch.setattr(diagnostics, "search", fake_search)
    assert diagnostics.main() == 0
    output = capsys.readouterr().out
    assert "OK: INEGI devolvió 1" in output
    assert secret not in output
    assert seen["token"] == secret


def test_diagnostic_redacts_server_token(monkeypatch, capsys):
    secret = "example-token-not-for-output"
    monkeypatch.setattr(settings, "BUILTIN_TOKEN", secret)
    monkeypatch.delenv("INEGI_DENUE_TOKEN", raising=False)
    def fake_search(*a, **kwargs):
        raise DenueError("Error: " + secret)
    monkeypatch.setattr(diagnostics, "search", fake_search)
    assert diagnostics.main() == 1
    output = capsys.readouterr().out
    assert secret not in output
    assert "[TOKEN OCULTO]" in output
