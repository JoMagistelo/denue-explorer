import sys
import pytest
from denue_explorer import settings

class Vault:
    def __init__(self): self.token = None
    def get_password(self, *_): return self.token
    def set_password(self, *args): self.token = args[-1]
    def delete_password(self, *_): self.token = None

def test_secure_local_token_lifecycle(monkeypatch):
    vault = Vault()
    monkeypatch.setitem(sys.modules, "keyring", vault)
    monkeypatch.delenv("INEGI_DENUE_TOKEN", raising=False)
    assert settings.load_token() == ""
    settings.save_token("valid-local-example-token")
    assert settings.load_token() == "valid-local-example-token"
    settings.delete_token()
    assert settings.load_token() == ""

def test_env_priority(monkeypatch):
    vault = Vault()
    vault.token = "stored"
    monkeypatch.setitem(sys.modules, "keyring", vault)
    monkeypatch.setenv("INEGI_DENUE_TOKEN", "from-env")
    assert settings.load_token() == "from-env"

def test_empty_token_rejected():
    with pytest.raises(settings.CredentialError):
        settings.save_token("")
