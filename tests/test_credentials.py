import pytest
from legends_dataforseo import Credentials, CredentialError, credential_status, load_credentials
from legends_dataforseo import client


@pytest.mark.parametrize("login_name", ["DATAFORSEO_LOGIN", "DATAFORSEO_USERNAME"])
def test_process_alias_and_secret_safe_repr(monkeypatch, login_name):
    monkeypatch.setenv(login_name, "fixture-login")
    monkeypatch.setenv("DATAFORSEO_PASSWORD", "fixture-secret")
    value = load_credentials()
    assert value.login == "fixture-login" and value.password == "fixture-secret"
    assert "fixture-login" not in repr(value) and "fixture-secret" not in repr(value)
    assert credential_status() == {"present": True, "source": "process-env"}


def test_user_environment_fallback(monkeypatch):
    values = {"DATAFORSEO_USERNAME": "fixture-user", "DATAFORSEO_PASSWORD": "fixture-secret"}
    monkeypatch.setattr(client, "_windows_user_environment", values.get)
    assert load_credentials().source == "user-env"


def test_partial_process_never_mixes_accounts(monkeypatch):
    monkeypatch.setenv("DATAFORSEO_LOGIN", "process-user")
    monkeypatch.setattr(client, "_windows_user_environment", lambda _: "user-value")
    with pytest.raises(CredentialError, match="Incomplete"):
        load_credentials()


def test_missing_credentials():
    with pytest.raises(CredentialError):
        load_credentials()
    assert credential_status()["present"] is False


@pytest.mark.parametrize("login,password", [("", "x"), ("x", ""), (None, "x"), ("x:y", "z")])
def test_invalid_explicit_credentials(login, password):
    with pytest.raises(CredentialError):
        Credentials(login, password)
