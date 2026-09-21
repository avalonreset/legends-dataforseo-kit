import pytest
from legends_dataforseo import client


@pytest.fixture(autouse=True)
def isolate_credentials_and_network(monkeypatch):
    for name in ("DATAFORSEO_LOGIN", "DATAFORSEO_USERNAME", "DATAFORSEO_PASSWORD"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(client, "_windows_user_environment", lambda _: None)
    monkeypatch.setattr(client, "_open", lambda *_: pytest.fail("Unexpected network request"))
