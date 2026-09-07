from monitor_service import Tenant, inspect_tenant


def test_alert_only_when_page_digest_changes(monkeypatch):
    monkeypatch.setattr("monitor_service.fetch_page", lambda url: "pricing v2")
    monkeypatch.setattr("monitor_service._request_embeddings", lambda text: [0.1, 0.2])
    tenant = Tenant("acme", "https://saas.example/pricing", "ops@acme.test")
    assert inspect_tenant(tenant, None) is None
    assert inspect_tenant(tenant, "old-digest") is not None

