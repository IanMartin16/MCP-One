from fastapi.testclient import TestClient

from app.main import app
from app.config.settings import get_settings

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_registry_modules_endpoint():
    response = client.get("/registry/modules")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_orchestrate_endpoint():
    response = client.post(
        "/orchestrate",
        json={
            "user_input": "Help me validate a CURP in Mexico"
        },
    )
    

    assert response.status_code == 200
    body = response.json()
    assert body["recommended_module"] == "curpify"
    assert body["mode"] in {"summary", "preview", "handoff", "composed_summary"}
    
def test_orchestrate_returns_reason_codes():
    response = client.post(
        "/orchestrate",
        json={"user_input": "Help me validate a CURP in Mexico"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "reason_codes" in body
    assert "matched_patterns" in body
    assert isinstance(body["reason_codes"], list)    

def test_active_provider_endpoint():
    response = client.get("/providers/active")
    assert response.status_code == 200
    body = response.json()
    assert "provider" in body
    assert "client_class" in body


def test_provider_generate_endpoint():
    response = client.post(
        "/providers/generate",
        json={
            "prompt": "Summarize current system status."
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "provider" in body
    assert "model" in body
    assert "content" in body
    assert body["success"] is True    

def test_reason_codes_meta_endpoint():
    response = client.get("/meta/reason-codes")
    assert response.status_code == 200
    body = response.json()
    assert "reason_codes" in body
    assert isinstance(body["reason_codes"], list)
    assert len(body["reason_codes"]) > 0    

def test_orchestrate_debug_endpoint():
    response = client.post(
        "/orchestrate/debug",
        json={
            "user_input": "Help me validate a CURP in Mexico"
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert "result" in body
    assert "debug" in body

    assert body["result"]["recommended_module"] == "curpify"
    assert body["debug"]["intent_family"] == "identity_validation"
    assert body["debug"]["rule_id"] is not None
    assert isinstance(body["debug"]["reason_codes"], list)
    assert isinstance(body["debug"]["reasoning_notes"], list)    

def test_orchestrate_debug_returns_plan():
    response = client.post(
        "/orchestrate/debug",
        json={
            "user_input": "Help me validate a CURP in Mexico"
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert "debug" in body
    assert "plan" in body["debug"]
    assert body["debug"]["plan"]["strategy"] == "single_module"    

def test_orchestrate_generates_request_id():
    response = client.post(
        "/orchestrate",
        json={
            "user_input": "Help me validate a CURP in Mexico"
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert "request_id" in body
    assert body["request_id"].startswith("mcp-")


def test_orchestrate_respects_external_request_id():
    response = client.post(
        "/orchestrate",
        json={
            "user_input": "Help me validate a CURP in Mexico",
            "request_id": "nexus-req-001"
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["request_id"] == "nexus-req-001"


def test_orchestrate_debug_contains_same_request_id():
    response = client.post(
        "/orchestrate/debug",
        json={
            "user_input": "Help me validate a CURP in Mexico",
            "request_id": "nexus-req-002"
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["result"]["request_id"] == "nexus-req-002"
    assert body["debug"]["request_id"] == "nexus-req-002"    

def test_orchestrate_debug_returns_execution_context():
    response = client.post(
        "/orchestrate/debug",
        json={
            "user_input": "Help me validate a CURP in Mexico",
            "request_id": "nexus-req-003",
            "client_context": {
                "source": "nexus",
                "channel": "widget",
                "session_id": "sess-003",
                "tenant": "evilink-dev",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert "debug" in body
    assert "execution_context" in body["debug"]
    assert body["debug"]["execution_context"]["request_id"] == "nexus-req-003"
    assert body["debug"]["execution_context"]["client_context"]["source"] == "nexus" 

def test_orchestrate_debug_returns_duration_fields():
    response = client.post(
        "/orchestrate/debug",
        json={
            "user_input": "Help me validate a CURP in Mexico",
            "request_id": "nexus-req-004",
            "client_context": {
                "source": "nexus",
                "channel": "widget",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()

    execution_context = body["debug"]["execution_context"]
    assert execution_context["started_at"] is not None
    assert execution_context["duration_ms"] is not None
    assert execution_context["duration_ms"] >= 0       

def test_meta_metrics_endpoint():
    response = client.get("/meta/metrics")
    assert response.status_code == 200

    body = response.json()
    assert "total_resolutions" in body
    assert "by_status" in body
    assert "by_mode" in body
    assert "by_plan_strategy" in body
    assert "by_recommended_module" in body
    assert "by_intent_family" in body
    assert "by_rule_id" in body
    assert "duration" in body
    assert "avg_ms" in body["duration"]
    assert "min_ms" in body["duration"]
    assert "max_ms" in body["duration"]

def test_meta_metrics_reset_endpoint():
    response = client.post("/meta/metrics/reset")
    assert response.status_code == 200
    assert response.json()["ok"] is True        

def test_meta_metrics_summary_endpoint():
    response = client.get("/meta/metrics/summary?limit=5")
    assert response.status_code == 200

    body = response.json()
    assert "total_resolutions" in body
    assert "duration" in body
    assert "avg_ms" in body["duration"]
    assert "min_ms" in body["duration"]
    assert "max_ms" in body["duration"]
    assert "top_statuses" in body
    assert "top_modes" in body
    assert "top_plan_strategies" in body
    assert "top_recommended_modules" in body
    assert "top_intent_families" in body
    assert "top_rule_ids" in body
    assert isinstance(body["top_statuses"], list)    

def test_recent_resolutions_endpoint():
    client.post(
        "/orchestrate",
        json={
            "user_input": "Help me validate a CURP in Mexico",
            "request_id": "recent-test-001",
            "client_context": {
                "source": "nexus",
                "channel": "widget",
            },
        },
    )

    response = client.get("/meta/recent-resolutions?limit=5")
    assert response.status_code == 200

    body = response.json()
    assert "items" in body
    assert isinstance(body["items"], list)
    assert len(body["items"]) >= 1

    item = body["items"][0]
    assert "request_id" in item
    assert "status" in item
    assert "recommended_module" in item
    assert "plan_strategy" in item    


def test_orchestrate_debug_disabled_returns_404(monkeypatch):
    monkeypatch.setenv("ENABLE_DEBUG_ROUTES", "false")
    get_settings.cache_clear()

    response = client.post(
        "/orchestrate/debug",
        json={"user_input": "Help me validate a CURP in Mexico"},
    )

    assert response.status_code == 404

    get_settings.cache_clear()


def test_metrics_disabled_returns_404(monkeypatch):
    monkeypatch.setenv("ENABLE_METRICS_ROUTES", "false")
    get_settings.cache_clear()

    response = client.get("/meta/metrics")

    assert response.status_code == 404

    get_settings.cache_clear()


def test_recent_resolutions_disabled_returns_404(monkeypatch):
    monkeypatch.setenv("ENABLE_RECENT_RESOLUTIONS_ROUTE", "false")
    get_settings.cache_clear()

    response = client.get("/meta/recent-resolutions")

    assert response.status_code == 404

    get_settings.cache_clear()    

def test_meta_metrics_endpoint():
    response = client.get("/meta/metrics")
    assert response.status_code == 200

    body = response.json()
    assert "total_resolutions" in body
    assert "by_status" in body
    assert "by_mode" in body
    assert "by_plan_strategy" in body
    assert "by_recommended_module" in body
    assert "by_intent_family" in body
    assert "by_rule_id" in body
    assert "duration" in body
    assert "provider_usage" in body

    assert "attempts" in body["provider_usage"]
    assert "successes" in body["provider_usage"]
    assert "failures" in body["provider_usage"]
    assert "by_provider" in body["provider_usage"]
    assert "by_model" in body["provider_usage"]

def test_meta_metrics_summary_endpoint():
    response = client.get("/meta/metrics/summary?limit=5")
    assert response.status_code == 200

    body = response.json()
    assert "total_resolutions" in body
    assert "duration" in body
    assert "provider_usage" in body
    assert "top_providers" in body["provider_usage"]
    assert "top_models" in body["provider_usage"]        