from app.metrics.recent_store import RecentResolutionStore


def test_recent_resolution_store_appends_and_lists():
    store = RecentResolutionStore(max_items=3)

    store.append({"request_id": "req-1"})
    store.append({"request_id": "req-2"})
    store.append({"request_id": "req-3"})

    items = store.list(limit=3)

    assert len(items) == 3
    assert items[0]["request_id"] == "req-3"
    assert items[1]["request_id"] == "req-2"
    assert items[2]["request_id"] == "req-1"


def test_recent_resolution_store_respects_max_items():
    store = RecentResolutionStore(max_items=2)

    store.append({"request_id": "req-1"})
    store.append({"request_id": "req-2"})
    store.append({"request_id": "req-3"})

    items = store.list(limit=10)

    assert len(items) == 2
    assert items[0]["request_id"] == "req-3"
    assert items[1]["request_id"] == "req-2"


def test_recent_resolution_store_reset():
    store = RecentResolutionStore(max_items=3)

    store.append({"request_id": "req-1"})
    store.reset()

    items = store.list(limit=10)

    assert items == []