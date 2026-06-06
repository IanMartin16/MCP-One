from app.metrics.provider_collector import record_provider_metrics
from app.metrics.store import metrics_store
from app.models.provider import ProviderResponse


def test_record_provider_metrics():
    metrics_store.reset()

    response = ProviderResponse(
        provider="openai",
        model="gpt-4.1-mini",
        content="Stub response",
        success=True,
        raw={"stub": True},
    )

    record_provider_metrics(response)

    snapshot = metrics_store.snapshot()

    assert snapshot["provider_usage"]["attempts"] == 1
    assert snapshot["provider_usage"]["successes"] == 1
    assert snapshot["provider_usage"]["failures"] == 0
    assert snapshot["provider_usage"]["by_provider"]["openai"] == 1
    assert snapshot["provider_usage"]["by_model"]["gpt-4.1-mini"] == 1