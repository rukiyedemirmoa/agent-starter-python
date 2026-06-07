"""Smoke tests for the web app: it wires up, the form renders, and the gate works.

Makes NO LLM/fal calls — only checks routing/templates and the password gate, so it's
fast and free. The cover endpoint (which spends) isn't exercised here; it's covered by
the band agent's own tests plus manual end-to-end.

We patch `agent.web.get_settings` so the gate behaves deterministically regardless of
whether your real .env has APP_PASSWORD set.
"""

import os

import pytest

# Fake key so agent construction at import is happy. No API call is made in these tests.
os.environ.setdefault("OPENROUTER_API_KEY", "test-key-not-real")


class _Settings:
    """Minimal stand-in exposing just what the web layer reads."""

    def __init__(self, app_password: str | None) -> None:
        self.app_password = app_password


def test_index_renders_the_vibe_form(monkeypatch: pytest.MonkeyPatch) -> None:
    from fastapi.testclient import TestClient

    from agent import web

    monkeypatch.setattr(web, "get_settings", lambda: _Settings(None))  # open app
    client = TestClient(web.app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Band Namer" in response.text
    assert 'hx-post="/band"' in response.text  # the vibe form is wired to the right route


def test_password_gate_redirects_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    from fastapi.testclient import TestClient

    from agent import web

    monkeypatch.setattr(web, "get_settings", lambda: _Settings("sekret"))  # gated app
    client = TestClient(web.app)
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"
