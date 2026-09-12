import pytest
from tools.safe_network import resolve_dns

def test_disallowed_target(monkeypatch):
    monkeypatch.setenv("ALLOWED_TARGETS", "localhost")
    with pytest.raises(ValueError): resolve_dns("example.org")

def test_allowed_localhost(monkeypatch):
    monkeypatch.setenv("ALLOWED_TARGETS", "localhost")
    assert resolve_dns("localhost")["host"] == "localhost"
