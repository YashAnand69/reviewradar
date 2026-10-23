"""A credential file alone must never advertise a running inference service."""

import httpx
import pytest
from fastapi.testclient import TestClient

from reviewradar.app import create_app
from reviewradar.config import Settings
from reviewradar.model import LocalModel


@pytest.fixture
def settings(tmp_path):
    return Settings(
        root=tmp_path,
        data_dir=tmp_path / "data",
        model_key_file=tmp_path / "key",
        api_token="a" * 40,
    )


def install_model_transport(monkeypatch, settings, handler):
    settings.model_key_file.write_text("private-test-key-never-returned")
    original = httpx.Client
    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kwargs: original(transport=httpx.MockTransport(handler), **kwargs),
    )


def test_missing_credentials_does_not_probe_or_claim_readiness(settings, monkeypatch):
    def unexpected_client(**kwargs):
        pytest.fail("Unconfigured model must not create a network client")

    monkeypatch.setattr(httpx, "Client", unexpected_client)
    result = LocalModel(settings).readiness()
    assert not result["ready"]
    assert "baseline" in result["reason"]


@pytest.mark.parametrize(
    "inventory",
    [
        {"data": [{"id": "different-model", "meta": {"n_ctx": 16384}}]},
        {"data": [{"id": "reviewradar-gemma4-e2b", "meta": {}}]},
        {"data": [{"id": "reviewradar-gemma4-e2b", "meta": {"n_ctx": True}}]},
        {"data": [{"id": "reviewradar-gemma4-e2b", "meta": {"n_ctx": 1024}}]},
        {"data": None},
    ],
)
def test_wrong_identity_or_unknown_context_stays_unavailable(
    settings, monkeypatch, inventory
):
    install_model_transport(
        monkeypatch, settings, lambda request: httpx.Response(200, json=inventory)
    )
    assert not LocalModel(settings).readiness()["ready"]


def test_readiness_uses_authenticated_inventory_without_generating(
    settings, monkeypatch
):
    paths = []

    def handler(request):
        paths.append(request.url.path)
        assert (
            request.headers["Authorization"] == "Bearer private-test-key-never-returned"
        )
        return httpx.Response(
            200, json={"data": [{"id": settings.model_name, "meta": {"n_ctx": 16384}}]}
        )

    install_model_transport(monkeypatch, settings, handler)
    result = LocalModel(settings).readiness()
    assert result["ready"]
    assert paths == ["/v1/models"]
    assert "private-test-key" not in str(result)


@pytest.mark.parametrize("failure", ["timeout", "refused", "unauthorized", "malformed"])
def test_unavailable_or_bad_service_is_recoverable(settings, monkeypatch, failure):
    def handler(request):
        if failure == "timeout":
            raise httpx.ReadTimeout("untrusted error with private details")
        if failure == "refused":
            raise httpx.ConnectError("untrusted error with private details")
        if failure == "unauthorized":
            return httpx.Response(
                401, json={"error": "untrusted error with private details"}
            )
        return httpx.Response(200, json=[None])

    install_model_transport(monkeypatch, settings, handler)
    result = LocalModel(settings).readiness()
    assert not result["ready"]
    assert "baseline" in result["reason"]
    assert "private details" not in str(result)


def test_health_keeps_app_usable_when_model_is_offline(settings, monkeypatch):
    monkeypatch.setattr(
        LocalModel,
        "readiness",
        lambda self: {"ready": False, "reason": "Model offline; baseline available."},
    )
    client = TestClient(create_app(settings), base_url="http://127.0.0.1:8893")
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["model_ready"] is False
    assert response.json()["model_configured"] is False
    assert "api_token" not in response.json()
