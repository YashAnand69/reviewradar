"""Saved reading history must remain reachable after repeated daily use."""

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
import pytest

from reviewradar.analysis import run_analysis
from reviewradar.app import create_app
from reviewradar.config import Settings
from reviewradar.schemas import normalize_snapshot


@pytest.fixture
def history(tmp_path):
    settings = Settings(
        root=tmp_path,
        data_dir=tmp_path / "data",
        api_token="a" * 40,
    )
    app = create_app(settings)
    snapshot = normalize_snapshot(
        {
            "fetched_at": "2026-10-23T11:00:00Z",
            "source": "synthetic",
            "owner": "Contributor",
            "complete": True,
            "warnings": [],
            "prs": [
                {
                    "id": "example/project#7",
                    "url": "https://github.com/example/project/pull/7",
                    "title": "The delivery fallback",
                    "author": "Contributor",
                    "state": "OPEN",
                    "fetched_at": "2026-10-23T11:00:00Z",
                    "complete": True,
                    "comments": [
                        {
                            "id": "comment:1",
                            "url": "https://github.com/example/project/pull/7#issuecomment-1",
                            "author": "Reviewer",
                            "is_bot": False,
                            "kind": "comment",
                            "body": "Please explain the fallback.",
                            "created_at": "2026-10-23T10:00:00Z",
                            "updated_at": "2026-10-23T10:00:00Z",
                        }
                    ],
                }
            ],
        }
    )
    store = app.state.store
    store.save_snapshot(snapshot)
    template = run_analysis(snapshot, "baseline", settings)
    client = TestClient(app, base_url="http://127.0.0.1:8893")
    client.headers.update({"X-ReviewRadar-Token": settings.api_token})
    return client, store, snapshot, template


def save_readings(store, template, count, *, same_time=False):
    start = datetime(2026, 10, 23, 12, tzinfo=timezone.utc)
    readings = []
    for number in range(count):
        created = start if same_time else start + timedelta(minutes=number)
        reading = template.model_copy(
            update={
                "id": f"reading-{number:03d}",
                "created_at": created.isoformat(),
            }
        )
        store.save_analysis(reading)
        readings.append(reading)
    return readings


def test_older_than_first_page_can_be_reopened_with_its_saved_note(history):
    client, store, snapshot, template = history
    readings = save_readings(store, template, 101)
    oldest = readings[0]
    store.set_disposition(
        oldest.id, oldest.cards[0].id, "reviewed", "Check the fallback next session."
    )

    first = client.get("/api/analyses")
    assert first.status_code == 200
    page = first.json()
    assert len(page) == 100
    assert page[0]["id"] == readings[-1].id
    assert oldest.id not in [item["id"] for item in page]
    assert page[0]["owner"] == snapshot.owner
    assert page[0]["fetched_at"] == snapshot.fetched_at
    assert page[0]["prs"] == [
        {
            "id": snapshot.prs[0].id,
            "title": snapshot.prs[0].title,
            "url": snapshot.prs[0].url,
        }
    ]
    assert page[0]["snapshot_id"] == snapshot.id
    assert page[0]["mode"] == "baseline"
    assert page[0]["card_count"] == 1
    assert page[0]["model"] is None

    older = client.get("/api/analyses", params={"before": page[-1]["id"]})
    assert older.status_code == 200
    assert [item["id"] for item in older.json()] == [oldest.id]
    reopened = client.get(f"/api/analyses/{oldest.id}")
    assert reopened.json() == oldest.model_dump()
    dispositions = client.get(f"/api/analyses/{oldest.id}/dispositions").json()
    assert dispositions[0]["state"] == "reviewed"
    assert dispositions[0]["note"] == "Check the fallback next session."
    assert store.get_snapshot(snapshot.id).model_dump() == snapshot.model_dump()


def test_equal_timestamps_page_by_identity_without_gaps_or_repetitions(history):
    client, store, _snapshot, template = history
    readings = save_readings(store, template, 205, same_time=True)
    expected = sorted((item.id for item in readings), reverse=True)
    received = []
    before = None
    page_lengths = []
    while True:
        params = {} if before is None else {"before": before}
        result = client.get("/api/analyses", params=params)
        assert result.status_code == 200
        page = result.json()
        if not page:
            break
        page_lengths.append(len(page))
        received.extend(item["id"] for item in page)
        before = page[-1]["id"]
    assert received == expected
    assert page_lengths == [100, 100, 5]
    assert len(set(received)) == len(readings)


def test_newer_insert_between_pages_does_not_shift_older_readings(history):
    client, store, _snapshot, template = history
    readings = save_readings(store, template, 101)
    page = client.get("/api/analyses").json()
    newest = template.model_copy(
        update={"id": "new-after-page", "created_at": "2026-10-24T12:00:00+00:00"}
    )
    store.save_analysis(newest)

    older = client.get("/api/analyses", params={"before": page[-1]["id"]}).json()
    assert [item["id"] for item in older] == [readings[0].id]
    assert not {item["id"] for item in older} & {item["id"] for item in page}
    assert client.get("/api/analyses").json()[0]["id"] == newest.id


def test_history_titles_and_capture_dates_stay_bound_to_each_snapshot(history):
    client, store, snapshot, template = history
    original = save_readings(store, template, 1)[0]
    refreshed_input = snapshot.model_dump()
    refreshed_input["fetched_at"] = "2026-10-24T11:00:00Z"
    refreshed_input["prs"][0]["fetched_at"] = refreshed_input["fetched_at"]
    refreshed_input["prs"][0]["title"] = "The revised delivery fallback"
    refreshed = normalize_snapshot(refreshed_input)
    store.save_snapshot(refreshed)
    second = template.model_copy(
        update={
            "id": "refreshed-reading",
            "snapshot_id": refreshed.id,
            "created_at": "2026-10-24T12:00:00+00:00",
        }
    )
    store.save_analysis(second)

    page = client.get("/api/analyses").json()
    assert [item["id"] for item in page] == [second.id, original.id]
    assert [item["fetched_at"] for item in page] == [
        refreshed.fetched_at,
        snapshot.fetched_at,
    ]
    assert [item["prs"][0]["title"] for item in page] == [
        refreshed.prs[0].title,
        snapshot.prs[0].title,
    ]
    assert store.get_analysis(original.id).snapshot_id == snapshot.id
    assert store.get_snapshot(snapshot.id).prs[0].title == snapshot.prs[0].title


@pytest.mark.parametrize("before", ["missing", "x' OR 1=1 --"])
def test_unknown_cursor_is_not_a_clean_empty_or_unfiltered_page(history, before):
    client, store, _snapshot, template = history
    save_readings(store, template, 1)
    response = client.get("/api/analyses", params={"before": before})
    assert response.status_code == 404
    assert response.json()["detail"].startswith("History cursor not found")
    assert len(client.get("/api/analyses").json()) == 1


@pytest.mark.parametrize("before", ["", "x" * 201])
def test_cursor_length_is_bounded_at_the_api_boundary(history, before):
    client, _store, _snapshot, _template = history
    response = client.get("/api/analyses", params={"before": before})
    assert response.status_code == 422


def test_empty_history_keeps_the_existing_array_contract(history):
    client, _store, _snapshot, _template = history
    assert client.get("/api/analyses").json() == []
