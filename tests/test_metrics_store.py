from app.metrics.store import MetricsStore


def test_metrics_store_records_values():
    store = MetricsStore()

    store.record(
        status="resolved",
        mode="summary",
        plan_strategy="single_module",
        recommended_module="curpify",
        intent_family="identity_validation",
        rule_id="rule_identity_validation_curpify",
    )

    snapshot = store.snapshot()

    assert snapshot["total_resolutions"] == 1
    assert snapshot["by_status"]["resolved"] == 1
    assert snapshot["by_mode"]["summary"] == 1
    assert snapshot["by_plan_strategy"]["single_module"] == 1
    assert snapshot["by_recommended_module"]["curpify"] == 1
    assert snapshot["by_intent_family"]["identity_validation"] == 1
    assert snapshot["by_rule_id"]["rule_identity_validation_curpify"] == 1


def test_metrics_store_reset():
    store = MetricsStore()

    store.record(
        status="resolved",
        mode="summary",
        plan_strategy="single_module",
        recommended_module="curpify",
        intent_family="identity_validation",
        rule_id="rule_identity_validation_curpify",
    )
    store.reset()

    snapshot = store.snapshot()

    assert snapshot["total_resolutions"] == 0
    assert snapshot["by_status"] == {}
    assert snapshot["by_mode"] == {}
    assert snapshot["by_plan_strategy"] == {}
    assert snapshot["by_recommended_module"] == {}
    assert snapshot["by_intent_family"] == {}
    assert snapshot["by_rule_id"] == {}

def test_metrics_store_summary_returns_sorted_items():
    store = MetricsStore()

    store.record(
        status="resolved",
        mode="summary",
        plan_strategy="single_module",
        recommended_module="curpify",
        intent_family="identity_validation",
        rule_id="rule_identity_validation_curpify",
    )
    store.record(
        status="resolved",
        mode="summary",
        plan_strategy="single_module",
        recommended_module="curpify",
        intent_family="identity_validation",
        rule_id="rule_identity_validation_curpify",
    )
    store.record(
        status="handoff_required",
        mode="handoff",
        plan_strategy="handoff",
        recommended_module="secure_link",
        intent_family="risk_evaluation",
        rule_id="rule_risk_eval_secure_preview",
    )

    summary = store.summary(limit=2)

    assert summary["total_resolutions"] == 3
    assert summary["top_statuses"][0]["key"] == "resolved"
    assert summary["top_statuses"][0]["count"] == 2
    assert summary["top_recommended_modules"][0]["key"] == "curpify"
    assert summary["top_intent_families"][0]["key"] == "identity_validation"    

def test_metrics_store_records_duration_stats():
    store = MetricsStore()

    store.record(
        status="resolved",
        mode="summary",
        plan_strategy="single_module",
        recommended_module="curpify",
        intent_family="identity_validation",
        rule_id="rule_identity_validation_curpify",
        duration_ms=10.0,
    )
    store.record(
        status="resolved",
        mode="summary",
        plan_strategy="single_module",
        recommended_module="curpify",
        intent_family="identity_validation",
        rule_id="rule_identity_validation_curpify",
        duration_ms=20.0,
    )
    store.record(
        status="handoff_required",
        mode="handoff",
        plan_strategy="handoff",
        recommended_module="secure_link",
        intent_family="risk_evaluation",
        rule_id="rule_risk_eval_secure_preview",
        duration_ms=40.0,
    )

    snapshot = store.snapshot()

    assert snapshot["duration"]["count"] == 3
    assert snapshot["duration"]["avg_ms"] == 23.33
    assert snapshot["duration"]["min_ms"] == 10.0
    assert snapshot["duration"]["max_ms"] == 40.0
    assert snapshot["duration"]["avg_by_status"]["resolved"] == 15.0
    assert snapshot["duration"]["avg_by_status"]["handoff_required"] == 40.0
    assert snapshot["duration"]["avg_by_mode"]["summary"] == 15.0
    assert snapshot["duration"]["avg_by_mode"]["handoff"] == 40.0    

def test_metrics_store_records_provider_usage():
    store = MetricsStore()

    store.record_provider_usage(
        provider="openai",
        model="gpt-4.1-mini",
        success=True,
    )
    store.record_provider_usage(
        provider="openai",
        model="gpt-4.1-mini",
        success=False,
    )
    store.record_provider_usage(
        provider="anthropic",
        model="claude-3-5-sonnet",
        success=True,
    )

    snapshot = store.snapshot()

    assert snapshot["provider_usage"]["attempts"] == 3
    assert snapshot["provider_usage"]["successes"] == 2
    assert snapshot["provider_usage"]["failures"] == 1
    assert snapshot["provider_usage"]["by_provider"]["openai"] == 2
    assert snapshot["provider_usage"]["by_provider"]["anthropic"] == 1
    assert snapshot["provider_usage"]["by_model"]["gpt-4.1-mini"] == 2
    assert snapshot["provider_usage"]["by_model"]["claude-3-5-sonnet"] == 1    