"""Compatibility and evidence-boundary tests for local model disagreements."""

import json
import sqlite3

from fastapi.testclient import TestClient
import pytest

from reviewradar.analysis import export_markdown, run_analysis
from reviewradar.app import create_app
from reviewradar.config import Settings
from reviewradar.schemas import Evidence, normalize_snapshot
from reviewradar.store import Store


@pytest.fixture
def evidence(tmp_path):
    settings = Settings(root=tmp_path, data_dir=tmp_path / "data", api_token="a" * 40)
    url = "https://github.com/example/project/pull/7"
    comments = [
        {"id": "r", "author": "reviewer", "body": "Please add a test.", "minute": 0},
        {"id": "a", "author": "owner", "body": "Added a test.", "minute": 1},
    ]
    snapshot = normalize_snapshot(
        {
            "fetched_at": "2026-10-23T11:00:00Z",
            "source": "synthetic",
            "owner": "owner",
            "complete": True,
            "warnings": [],
            "prs": [
                {
                    "id": "example/project#7",
                    "url": url,
                    "title": "Synthetic migration fixture",
                    "author": "owner",
                    "state": "OPEN",
                    "fetched_at": "2026-10-23T11:00:00Z",
                    "complete": True,
                    "comments": [
                        {
                            "id": c["id"],
                            "url": f"{url}#issuecomment-{i + 1}",
                            "author": c["author"],
                            "body": c["body"],
                            "is_bot": False,
                            "kind": "comment",
                            "created_at": f"2026-10-23T10:0{c['minute']}:00Z",
                            "updated_at": f"2026-10-23T10:0{c['minute']}:00Z",
                        }
                        for i, c in enumerate(comments)
                    ],
                }
            ],
        }
    )
    analysis = run_analysis(snapshot, "baseline", settings)
    analysis.mode = "model"
    analysis.cards[0].response = Evidence(comment_id="a", quote="Added a test.")
    analysis.cards[0].interpretation = "possibly_responded"
    return settings, snapshot, analysis


def old_database(settings, snapshot, analysis):
    settings.data_dir.mkdir(parents=True)
    path = settings.data_dir / "reviewradar.sqlite3"
    with sqlite3.connect(path) as db:
        db.executescript("""
            CREATE TABLE snapshots (id TEXT PRIMARY KEY, fetched_at TEXT NOT NULL,
                owner TEXT NOT NULL, payload TEXT NOT NULL);
            CREATE TABLE analyses (id TEXT PRIMARY KEY, snapshot_id TEXT NOT NULL REFERENCES snapshots(id),
                created_at TEXT NOT NULL, mode TEXT NOT NULL, payload TEXT NOT NULL);
            CREATE TABLE dispositions (analysis_id TEXT NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
                card_id TEXT NOT NULL, state TEXT NOT NULL, note TEXT NOT NULL,
                updated_at TEXT NOT NULL, PRIMARY KEY (analysis_id, card_id));
        """)
        db.execute(
            "INSERT INTO snapshots VALUES (?, ?, ?, ?)",
            (
                snapshot.id,
                snapshot.fetched_at,
                snapshot.owner,
                snapshot.model_dump_json(),
            ),
        )
        db.execute(
            "INSERT INTO analyses VALUES (?, ?, ?, ?, ?)",
            (
                analysis.id,
                snapshot.id,
                analysis.created_at,
                analysis.mode,
                analysis.model_dump_json(),
            ),
        )
        db.execute(
            "INSERT INTO dispositions VALUES (?, ?, ?, ?, ?)",
            (
                analysis.id,
                analysis.cards[0].id,
                "reviewed",
                "Keep my original note",
                analysis.created_at,
            ),
        )
    return path


def populated(evidence):
    settings, snapshot, analysis = evidence
    store = Store(settings.data_dir)
    store.save_snapshot(snapshot)
    store.save_analysis(analysis)
    return settings, snapshot, analysis, store


def test_old_database_migrates_without_changing_rows_or_evidence(evidence):
    settings, snapshot, analysis = evidence
    path = old_database(settings, snapshot, analysis)
    for _ in range(2):
        store = Store(settings.data_dir)
        saved = store.dispositions(analysis.id)[0]
        assert (saved.state, saved.note, saved.updated_at, saved.assessment) == (
            "reviewed",
            "Keep my original note",
            analysis.created_at,
            "unassessed",
        )
        assert store.get_snapshot(snapshot.id).model_dump() == snapshot.model_dump()
        assert store.get_analysis(analysis.id).model_dump() == analysis.model_dump()
    with sqlite3.connect(path) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 1
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []


def test_future_database_is_rejected_before_any_mutation(tmp_path):
    path = tmp_path / "reviewradar.sqlite3"
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE future_data (payload TEXT)")
        db.execute("INSERT INTO future_data VALUES ('keep')")
        db.execute("PRAGMA user_version = 2")
        before = db.execute("SELECT name, sql FROM sqlite_master").fetchall()
    with pytest.raises(ValueError, match="newer ReviewRadar"):
        Store(tmp_path)
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT name, sql FROM sqlite_master").fetchall() == before
        assert db.execute("SELECT payload FROM future_data").fetchone()[0] == "keep"
        assert db.execute("PRAGMA user_version").fetchone()[0] == 2


def test_inconsistent_version_marker_is_rejected_without_silent_repair(evidence):
    settings, snapshot, analysis = evidence
    path = old_database(settings, snapshot, analysis)
    with sqlite3.connect(path) as db:
        db.execute("PRAGMA user_version = 1")
    with pytest.raises(ValueError, match="incomplete"):
        Store(settings.data_dir)
    with sqlite3.connect(path) as db:
        assert "assessment" not in {
            row[1] for row in db.execute("PRAGMA table_info(dispositions)")
        }
        assert (
            db.execute("SELECT note FROM dispositions").fetchone()[0]
            == "Keep my original note"
        )


def test_failed_migration_rolls_back_column_and_version(evidence, monkeypatch):
    settings, snapshot, analysis = evidence
    path = old_database(settings, snapshot, analysis)
    real_connect = sqlite3.connect

    class FailureAtVersion(sqlite3.Connection):
        def execute(self, sql, *args, **kwargs):
            if sql.startswith("PRAGMA user_version ="):
                raise sqlite3.OperationalError("Simulated migration failure")
            return super().execute(sql, *args, **kwargs)

    monkeypatch.setattr(
        "reviewradar.store.sqlite3.connect",
        lambda *args, **kwargs: real_connect(*args, factory=FailureAtVersion, **kwargs),
    )
    with pytest.raises(sqlite3.OperationalError, match="Simulated"):
        Store(settings.data_dir)
    with real_connect(path) as db:
        assert "assessment" not in {
            row[1] for row in db.execute("PRAGMA table_info(dispositions)")
        }
        assert db.execute("PRAGMA user_version").fetchone()[0] == 0
        assert (
            db.execute("SELECT note FROM dispositions").fetchone()[0]
            == "Keep my original note"
        )


def test_assessment_state_and_notes_are_independent_and_resettable(evidence):
    _settings, _snapshot, analysis, store = populated(evidence)
    card = analysis.cards[0]
    store.set_disposition(analysis.id, card.id, "open", "Inspect", "not_a_request")
    updated = store.set_disposition(analysis.id, card.id, "reviewed", "Checked")
    assert (updated.assessment, updated.state, updated.note) == (
        "not_a_request",
        "reviewed",
        "Checked",
    )
    reopened = store.set_disposition(
        analysis.id, card.id, "open", "Checked", "unassessed"
    )
    assert (reopened.assessment, reopened.state, reopened.note) == (
        "unassessed",
        "open",
        "Checked",
    )
    store.set_disposition(analysis.id, card.id, "open", "Checked", "reply_not_relevant")
    assert (
        Store(store.path.parent).dispositions(analysis.id)[0].assessment
        == "reply_not_relevant"
    )


def test_api_legacy_omission_preserves_assessment_but_explicit_reset_clears(evidence):
    settings, _snapshot, analysis, _store = populated(evidence)
    app = create_app(settings)
    route = f"/api/analyses/{analysis.id}/cards/{analysis.cards[0].id}/disposition"
    with TestClient(app, base_url="http://127.0.0.1:8893") as client:
        client.headers.update(
            {
                "X-ReviewRadar-Token": settings.api_token,
                "Origin": "http://127.0.0.1:8893",
            }
        )
        for body, expected in [
            ({"state": "open", "note": "Original legacy client"}, "unassessed"),
            (
                {"state": "open", "note": "First", "assessment": "not_a_request"},
                "not_a_request",
            ),
            ({"state": "reviewed", "note": "Legacy note"}, "not_a_request"),
            (
                {
                    "state": "reviewed",
                    "note": "Legacy note",
                    "assessment": "unassessed",
                },
                "unassessed",
            ),
        ]:
            response = client.put(route, json=body)
            assert response.status_code == 200
            assert response.json()["assessment"] == expected
        assert (
            client.get(f"/api/analyses/{analysis.id}/dispositions").json()[0]["note"]
            == "Legacy note"
        )
        for invalid in [None, "accepted", 1]:
            assert (
                client.put(
                    route, json={"state": "open", "assessment": invalid}
                ).status_code
                == 422
            )


@pytest.mark.parametrize(
    "mode,has_response,assessment",
    [
        ("baseline", False, "not_a_request"),
        ("baseline", False, "reply_not_relevant"),
        ("model", False, "reply_not_relevant"),
    ],
)
def test_inapplicable_assessments_are_rejected_without_writing(
    evidence, mode, has_response, assessment
):
    settings, snapshot, analysis = evidence
    analysis.mode = mode
    if not has_response:
        analysis.cards[0].response = None
    store = Store(settings.data_dir)
    store.save_snapshot(snapshot)
    store.save_analysis(analysis)
    with pytest.raises(ValueError):
        store.set_disposition(
            analysis.id, analysis.cards[0].id, "reviewed", "Should not save", assessment
        )
    assert store.dispositions(analysis.id) == []
    assert (
        store.set_disposition(
            analysis.id, analysis.cards[0].id, "open", "", "unassessed"
        ).assessment
        == "unassessed"
    )


def test_disagreement_export_is_local_and_original_analysis_is_immutable(evidence):
    _settings, snapshot, analysis, store = populated(evidence)
    before = analysis.model_dump_json()
    note = "[forged](https://evil.example)\n<script>bad()</script>\n# heading"
    store.set_disposition(
        analysis.id, analysis.cards[0].id, "open", note, "reply_not_relevant"
    )
    output = export_markdown(analysis, snapshot, store.dispositions(analysis.id))
    assert "Human assessment (local): Reply not relevant" in output
    assert "does not alter the original model output or GitHub" in output
    assert "Interpretation: possibly_responded" in output
    assert "Unverified model explanation:" in output
    assert (
        "[Possible later response](https://github.com/example/project/pull/7#issuecomment-2)"
        in output
    )
    assert "[forged](https://evil.example)" not in output
    assert "<script>" not in output
    assert "\n# heading" not in output
    assert json.loads(store.get_analysis(analysis.id).model_dump_json()) == json.loads(
        before
    )
    other = analysis.model_copy(deep=True)
    other.id = "different-analysis"
    store.save_analysis(other)
    assert store.dispositions(other.id) == []


def test_api_rejects_inapplicable_assessment_with_actionable_message(evidence):
    settings, _snapshot, analysis, store = populated(evidence)
    empty_response = analysis.model_copy(deep=True)
    empty_response.id = "no-response"
    empty_response.cards[0].response = None
    store.save_analysis(empty_response)
    with TestClient(create_app(settings), base_url="http://127.0.0.1:8893") as client:
        client.headers.update(
            {
                "X-ReviewRadar-Token": settings.api_token,
                "Origin": "http://127.0.0.1:8893",
            }
        )
        response = client.put(
            f"/api/analyses/{empty_response.id}/cards/{analysis.cards[0].id}/disposition",
            json={"state": "open", "assessment": "reply_not_relevant"},
        )
        assert response.status_code == 422
        assert "possible response" in response.json()["detail"]
        assert store.dispositions(empty_response.id) == []
