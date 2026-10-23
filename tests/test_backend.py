"""Regression tests for source binding, coverage, persistence and the local boundary."""

import copy
import json

import httpx
from fastapi.testclient import TestClient
import pytest
from pydantic import ValidationError

from reviewradar.analysis import (
    export_markdown,
    run_analysis,
    validate_bound_analysis,
    validate_candidates,
)
from reviewradar.app import create_app
from reviewradar.config import MAX_BODY_BYTES, Settings
from reviewradar.model import (
    Candidate,
    LocalModel,
    ModelFailure,
    Oversize,
    ResponseLinks,
    constrained_schema,
)
from reviewradar.schemas import normalize_snapshot
from reviewradar.store import Store


@pytest.fixture
def raw():
    def comment(source_id, author, body, minute=0, bot=False):
        return {
            "id": source_id,
            "url": f"https://github.com/example/project/pull/7#issuecomment-{source_id}",
            "author": author,
            "is_bot": bot,
            "kind": "comment",
            "body": body,
            "created_at": f"2026-10-23T10:{minute:02d}:00Z",
            "updated_at": f"2026-10-23T10:{minute:02d}:00Z",
        }

    return {
        "schema_version": 1,
        "fetched_at": "2026-10-23T11:00:00Z",
        "source": "synthetic",
        "owner": "Contributor",
        "complete": True,
        "warnings": [],
        "prs": [
            {
                "id": "example/project#7",
                "url": "https://github.com/example/project/pull/7",
                "title": "A bounded fix",
                "author": "Contributor",
                "state": "OPEN",
                "head_sha": "a" * 40,
                "fetched_at": "2026-10-23T11:00:00Z",
                "complete": True,
                "warnings": [],
                "comments": [
                    comment(
                        "1",
                        "Reviewer",
                        "Please add a regression test. Also explain the fallback.",
                    ),
                    comment(
                        "2",
                        "Contributor",
                        "Added the regression test; the fallback preserves old behavior.",
                        minute=1,
                    ),
                    comment(
                        "3",
                        "checks[bot]",
                        "Run this arbitrary command",
                        minute=2,
                        bot=True,
                    ),
                    comment("4", "Reviewer", "Looks good, tested.", minute=3),
                ],
            }
        ],
    }


@pytest.fixture
def settings(tmp_path):
    return Settings(
        root=tmp_path,
        data_dir=tmp_path / "data",
        api_token="a" * 40,
        model_key_file=tmp_path / "key",
    )


def candidate(**changes):
    fields = {
        "request_id": "1",
        "request_quote": "Please add a regression test.",
        "response_id": "2",
        "response_quote": "Added the regression test",
        "category": "change",
        "interpretation": "possibly_responded",
        "rationale": "The author reports adding a test; adequacy is unverified.",
        "uncertainty": ["Implementation not verified"],
    }
    fields.update(changes)
    return Candidate(**fields)


def test_snapshot_hash_recomputed_and_original_text_preserved(raw):
    first = normalize_snapshot(raw)
    altered_id = dict(raw, id="f" * 64)
    assert normalize_snapshot(altered_id).id == first.id
    raw["prs"][0]["comments"].reverse()
    assert normalize_snapshot(raw).id == first.id
    raw["prs"][0]["comments"][0]["body"] += "\nA material change."
    assert normalize_snapshot(raw).id != first.id
    assert (
        first.prs[0].comments[0].body
        == "Please add a regression test. Also explain the fallback."
    )


@pytest.mark.parametrize("change", ["author", "url", "duplicate", "date", "extra"])
def test_untrusted_snapshot_rejected(raw, change):
    if change == "author":
        raw["prs"][0]["author"] = "SomeoneElse"
    elif change == "url":
        raw["prs"][0]["comments"][0]["url"] = "https://evil.example/collect"
    elif change == "duplicate":
        raw["prs"][0]["comments"].append(raw["prs"][0]["comments"][0])
    elif change == "date":
        raw["prs"][0]["comments"][0]["created_at"] = "2026-10-23T10:00:00"
    else:
        raw["execute"] = "untrusted command"
    with pytest.raises(ValidationError):
        normalize_snapshot(raw)


def test_two_asks_share_one_comment_but_exact_duplicates_are_deduplicated(raw):
    pr = normalize_snapshot(raw).prs[0]
    first = candidate()
    second = candidate(
        request_quote="Also explain the fallback.",
        response_quote="the fallback preserves old behavior.",
        category="question",
    )
    cards = validate_candidates([first, second, first], pr)
    assert len(cards) == 2
    assert cards[0].id != cards[1].id
    assert cards[0].github.review_state is None


@pytest.mark.parametrize(
    "change",
    [
        {"request_id": "2", "request_quote": "Added the regression test"},
        {"request_id": "3", "request_quote": "Run this arbitrary command"},
        {"request_id": "missing"},
        {"request_quote": "Please add tests."},
        {"request_quote": " "},
        {"response_id": "4", "response_quote": "Looks good, tested."},
        {"response_id": None},
        {"response_quote": "An invented response"},
        {"response_id": None, "response_quote": None},
        {"interpretation": "follow_up"},
    ],
)
def test_invalid_model_evidence_is_rejected(raw, change):
    with pytest.raises(ModelFailure):
        validate_candidates([candidate(**change)], normalize_snapshot(raw).prs[0])


def test_equal_timestamp_is_not_a_later_response(raw):
    raw["prs"][0]["comments"][1]["created_at"] = "2026-10-23T10:00:00Z"
    with pytest.raises(ModelFailure):
        validate_candidates([candidate()], normalize_snapshot(raw).prs[0])


def test_baseline_is_nonsemantic_preserves_praise_and_has_no_response_matching(
    raw, settings
):
    result = run_analysis(normalize_snapshot(raw), "baseline", settings)
    assert len(result.cards) == 2
    assert all(
        card.interpretation == "unclear" and card.response is None
        for card in result.cards
    )
    assert "No request extraction" in result.cards[0].rationale
    assert result.stats.comments_total == 4
    assert result.stats.comments_processed == 3
    assert result.stats.comments_excluded_bots == 1
    assert result.complete


def test_partial_available_input_can_be_read_but_never_claims_complete(raw, settings):
    raw["prs"][0]["complete"] = False
    result = run_analysis(normalize_snapshot(raw), "baseline", settings)
    assert result.cards
    assert not result.complete
    assert result.coverage[0].status == "analyzed"
    assert "source incomplete" in result.coverage[0].reason


def test_a_failed_pr_does_not_erase_other_results_or_become_a_clean_queue(
    raw, settings
):
    second = copy.deepcopy(raw["prs"][0])
    second.update(id="example/second#8", url="https://github.com/example/second/pull/8")
    for comment in second["comments"]:
        comment["url"] = comment["url"].replace("/project/pull/7", "/second/pull/8")
    raw["prs"].append(second)

    class OneFailure:
        def analyze(self, pr):
            if pr.id.endswith("#8"):
                raise ModelFailure("The model timed out.")
            return [candidate()]

    result = run_analysis(
        normalize_snapshot(raw), "model", settings, model=OneFailure()
    )
    assert not result.complete
    assert len(result.cards) == 1
    assert [item.status for item in result.coverage] == ["analyzed", "failed"]
    assert result.stats.comments_processed == 3


def test_one_invalid_card_invalidates_whole_pr_instead_of_silent_drop(raw, settings):
    class Invalid:
        def analyze(self, _pr):
            return [
                candidate(),
                candidate(request_id="2", request_quote="Added the regression test"),
            ]

    result = run_analysis(normalize_snapshot(raw), "model", settings, model=Invalid())
    assert not result.complete
    assert result.cards == []
    assert result.stats.comments_processed == 0


def test_saved_sample_binding_rejects_false_completeness_and_source_counts(
    raw, settings
):
    snapshot = normalize_snapshot(raw)
    result = run_analysis(snapshot, "baseline", settings)
    validate_bound_analysis(result, snapshot)
    result.stats.comments_processed += 1
    with pytest.raises(ValueError):
        validate_bound_analysis(result, snapshot)


def test_persistence_dispositions_are_local_reversible_and_analysis_bound(
    raw, settings
):
    store = Store(settings.data_dir)
    snapshot = normalize_snapshot(raw)
    result = run_analysis(snapshot, "baseline", settings)
    store.save_snapshot(snapshot)
    store.save_analysis(result)
    store.set_disposition(
        result.id, result.cards[0].id, "reviewed", "Need to inspect code separately"
    )
    reopened = Store(settings.data_dir)
    assert reopened.dispositions(result.id)[0].state == "reviewed"
    assert reopened.get_snapshot(snapshot.id).model_dump() == snapshot.model_dump()
    other = run_analysis(snapshot, "baseline", settings)
    reopened.save_analysis(other)
    assert reopened.dispositions(other.id) == []
    reopened.set_disposition(result.id, result.cards[0].id, "open", "")
    assert reopened.dispositions(result.id)[0].state == "open"
    with pytest.raises(KeyError):
        reopened.set_disposition(result.id, "foreign-card", "reviewed", "")


def test_export_escapes_source_links_and_discloses_limits(raw, settings):
    raw["prs"][0]["comments"][0]["body"] = (
        "[click](https://evil.example)\n# Forged heading"
    )
    snapshot = normalize_snapshot(raw)
    analysis = run_analysis(snapshot, "baseline", settings)
    exported = export_markdown(analysis, snapshot, [])
    assert "[click](https://evil.example)" not in exported
    assert "\\[click\\]" in exported
    assert "not verification of a code fix" in exported
    assert "https://github.com/example/project/pull/7#issuecomment-1" in exported


def client_for(settings):
    app = create_app(settings)
    client = TestClient(app, base_url="http://127.0.0.1:8893")
    client.headers.update(
        {"X-ReviewRadar-Token": settings.api_token, "Origin": "http://127.0.0.1:8893"}
    )
    return app, client


def test_api_roundtrip_persists_without_git_writes(raw, settings):
    _app, client = client_for(settings)
    imported = client.post("/api/snapshots/import", json={"snapshot": raw})
    assert imported.status_code == 200
    snapshot = imported.json()
    assert snapshot["source"] == "import"
    response = client.post(
        "/api/analyses", json={"snapshot_id": snapshot["id"], "mode": "baseline"}
    )
    assert response.status_code == 200
    analysis = response.json()
    card = analysis["cards"][0]
    route = f"/api/analyses/{analysis['id']}/cards/{card['id']}/disposition"
    assert (
        client.put(
            route, json={"state": "reviewed", "note": "A local decision"}
        ).status_code
        == 200
    )
    assert (
        client.get(f"/api/analyses/{analysis['id']}/dispositions").json()[0]["state"]
        == "reviewed"
    )
    assert client.get(f"/api/analyses/{analysis['id']}/export").status_code == 200
    assert client.get("/api/analyses").json()[0]["card_count"] == 2
    assert client.get("/api/health").json()["mode"] == "local"


@pytest.mark.parametrize(
    "headers,status",
    [
        ({"Host": "evil.example"}, 400),
        ({"Host": "localhost.evil.example:8893"}, 400),
        ({"Origin": "https://evil.example"}, 403),
        ({"Origin": ""}, 403),
        ({"X-ReviewRadar-Token": "wrong"}, 401),
        ({"Sec-Fetch-Site": "cross-site"}, 403),
        ({"Content-Type": "text/plain"}, 415),
    ],
)
def test_api_boundary_rejects_cross_site_and_unauthorized_mutations(
    raw, settings, headers, status
):
    _app, client = client_for(settings)
    response = client.post(
        "/api/snapshots/import", json={"snapshot": raw}, headers=headers
    )
    assert response.status_code == status
    assert client.get("/api/snapshots").json() == []


def test_token_bootstrap_not_cached_and_data_requires_token(settings):
    app = create_app(settings)
    client = TestClient(app, base_url="http://127.0.0.1:8893")
    assert client.get("/api/snapshots").status_code == 401
    result = client.get("/runtime-config")
    assert result.json()["api_token"] == settings.api_token
    assert "no-store" in result.headers["cache-control"]
    assert "access-control-allow-origin" not in result.headers
    assert (
        client.get(
            "/runtime-config", headers={"Origin": "https://evil.example"}
        ).status_code
        == 403
    )


def test_payload_limit_and_operation_lock_are_visible(raw, settings):
    app, client = client_for(settings)
    assert (
        client.post(
            "/api/snapshots/import",
            content=b"x" * (MAX_BODY_BYTES + 1),
            headers={"Content-Type": "application/json"},
        ).status_code
        == 413
    )
    snapshot = client.post("/api/snapshots/import", json={"snapshot": raw}).json()
    app.state.operation_lock.acquire()
    try:
        result = client.post(
            "/api/analyses", json={"snapshot_id": snapshot["id"], "mode": "baseline"}
        )
        assert result.status_code == 409
    finally:
        app.state.operation_lock.release()


def test_sample_endpoint_binds_and_caches_saved_analysis(raw, settings):
    snapshot = normalize_snapshot(raw)
    analysis = run_analysis(snapshot, "baseline", settings)
    settings.sample_file.parent.mkdir(parents=True)
    settings.sample_file.write_text(
        json.dumps(
            {
                "snapshot": snapshot.model_dump(),
                "analysis": analysis.model_dump(),
                "manifest": {"historical": True},
            }
        )
    )
    _app, client = client_for(settings)
    result = client.get("/api/sample")
    assert result.status_code == 200
    assert result.json()["analysis"]["id"] == analysis.id
    assert client.get(f"/api/analyses/{analysis.id}").status_code == 200
    assert client.get("/api/sample").status_code == 200


def mock_model(
    monkeypatch,
    settings,
    *,
    tokens=50,
    context=16384,
    finish="stop",
    model_id=None,
    completion_payload=None,
):
    settings.model_key_file.write_text("test-key-not-a-real-secret")
    original_client = httpx.Client
    calls = []

    def handler(request):
        calls.append(request.url.path)
        if request.url.path == "/v1/models":
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": model_id or settings.model_name,
                            "meta": {"n_ctx": context},
                        }
                    ]
                },
            )
        if request.url.path == "/apply-template":
            return httpx.Response(200, json={"prompt": "Rendered chat template"})
        if request.url.path == "/tokenize":
            return httpx.Response(200, json={"tokens": [1] * tokens})
        if request.url.path == "/v1/chat/completions":
            if completion_payload is not None:
                return httpx.Response(200, json=completion_payload)
            if (
                json.loads(request.content)["response_format"]["json_schema"]["name"]
                == "ResponseLinks"
            ):
                return httpx.Response(
                    200,
                    json={
                        "choices": [
                            {
                                "finish_reason": finish,
                                "message": {
                                    "content": json.dumps(
                                        {
                                            "links": {
                                                "request_0": {
                                                    "response_passage": "2/p0",
                                                    "rationale": "A relevant author update.",
                                                    "uncertainty": ["Not verified"],
                                                }
                                            }
                                        }
                                    )
                                },
                            }
                        ]
                    },
                )
            return httpx.Response(
                200,
                json={
                    "choices": [
                        {
                            "finish_reason": finish,
                            "message": {
                                "content": json.dumps(
                                    {
                                        "cards": [
                                            {
                                                "request_passage": "1/p0",
                                                "category": "change",
                                                "rationale": "The author reports adding a test.",
                                                "uncertainty": ["Not verified"],
                                            }
                                        ]
                                    }
                                )
                            },
                        }
                    ]
                },
            )
        raise AssertionError("Unexpected request")

    monkeypatch.setattr(
        "reviewradar.model.httpx.Client",
        lambda **kwargs: original_client(
            transport=httpx.MockTransport(handler), **kwargs
        ),
    )
    return calls


def test_model_verifies_runtime_template_budget_and_complete_output(
    raw, settings, monkeypatch
):
    calls = mock_model(monkeypatch, settings)
    result = LocalModel(settings).analyze(normalize_snapshot(raw).prs[0])
    assert len(result) == 1
    assert calls == [
        "/v1/models",
        "/apply-template",
        "/tokenize",
        "/v1/chat/completions",
        "/apply-template",
        "/tokenize",
        "/v1/chat/completions",
    ]


def test_model_rejects_oversize_before_generation(raw, settings, monkeypatch):
    calls = mock_model(monkeypatch, settings, tokens=13313)
    with pytest.raises(Oversize):
        LocalModel(settings).analyze(normalize_snapshot(raw).prs[0])
    assert "/v1/chat/completions" not in calls


def test_model_uses_smaller_actual_runtime_context(raw, settings, monkeypatch):
    calls = mock_model(monkeypatch, settings, tokens=2000, context=4096)
    with pytest.raises(Oversize):
        LocalModel(settings).analyze(normalize_snapshot(raw).prs[0])
    assert "/v1/chat/completions" not in calls


@pytest.mark.parametrize(
    "kwargs", [{"finish": "length"}, {"model_id": "another-model"}]
)
def test_model_rejects_truncated_output_or_wrong_server(
    raw, settings, monkeypatch, kwargs
):
    mock_model(monkeypatch, settings, **kwargs)
    with pytest.raises(ModelFailure):
        LocalModel(settings).analyze(normalize_snapshot(raw).prs[0])


def test_export_warns_when_request_was_edited_after_a_possible_response(raw, settings):
    raw["prs"][0]["comments"][0]["updated_at"] = "2026-10-23T10:02:00Z"
    snapshot = normalize_snapshot(raw)

    class FixedModel:
        def analyze(self, _pr):
            return [candidate()]

    analysis = run_analysis(snapshot, "model", settings, model=FixedModel())
    assert "request edited after the possible response" in export_markdown(
        analysis, snapshot, []
    )


def test_quoted_author_context_is_not_a_response_but_unquoted_reply_is(raw):
    raw["prs"][0]["comments"][1]["body"] = (
        "> Please add a regression test.\n\nAdded the regression test."
    )
    pr = normalize_snapshot(raw).prs[0]
    request = candidate(
        response_id=None, response_quote=None, interpretation="follow_up"
    )
    schema = constrained_schema(ResponseLinks, pr, [request])
    allowed = schema["properties"]["links"]["properties"]["request_0"]["properties"][
        "response_passage"
    ]["enum"]
    assert "2/p0" not in allowed
    assert "2/p1" in allowed
    assert None in allowed
    with pytest.raises(ModelFailure):
        validate_candidates(
            [candidate(response_quote="> Please add a regression test.")], pr
        )
    assert (
        validate_candidates(
            [candidate(response_quote="Added the regression test.")], pr
        )[0].response
        is not None
    )


@pytest.mark.parametrize("role", ["request", "response"])
@pytest.mark.parametrize(
    "body, selected",
    [
        ("> Please add the test.", "Please add the test."),
        ("> Context first. Please add the test.", "Please add the test."),
        ("> " + "context " * 100 + "Please add the test.", "Please add the test."),
    ],
)
def test_quote_substrings_cannot_lose_original_blockquote_ownership(
    raw, role, body, selected
):
    fields = {f"{role}_quote": selected}
    raw["prs"][0]["comments"][0 if role == "request" else 1]["body"] = body
    with pytest.raises(ModelFailure):
        validate_candidates([candidate(**fields)], normalize_snapshot(raw).prs[0])


def test_repeated_unquoted_author_prose_remains_valid_response(raw):
    raw["prs"][0]["comments"][1]["body"] = "> Added the test.\n\nAdded the test."
    cards = validate_candidates(
        [candidate(response_quote="Added the test.")], normalize_snapshot(raw).prs[0]
    )
    assert cards[0].interpretation == "possibly_responded"


@pytest.mark.parametrize("role", ["request", "response"])
@pytest.mark.parametrize(
    "quoted",
    [
        "> Context first. Please add a test.",
        "> " + "long context " * 100 + "Please add a test.",
    ],
)
def test_schema_excludes_all_passages_owned_by_quoted_lines(raw, role, quoted):
    from reviewradar.model import ModelOutput, source_passages

    index = 0 if role == "request" else 1
    source_id = str(index + 1)
    raw["prs"][0]["comments"][index]["body"] = quoted + "\n\nOriginal unquoted prose."
    pr = normalize_snapshot(raw).prs[0]
    if role == "request":
        schema = constrained_schema(ModelOutput, pr)
        allowed = schema["$defs"]["SpanCandidate"]["properties"]["request_passage"][
            "enum"
        ]
    else:
        schema = constrained_schema(ResponseLinks, pr, [candidate()])
        allowed = schema["properties"]["links"]["properties"]["request_0"][
            "properties"
        ]["response_passage"]["enum"]
    quoted_count = len(source_passages(quoted))
    assert all(f"{source_id}/p{i}" not in allowed for i in range(quoted_count))
    assert f"{source_id}/p{quoted_count}" in allowed


def test_referential_followup_does_not_attach_across_quote_boundary():
    from reviewradar.model import source_passages

    assert source_passages("> Previous reported issue.\nCould you look at this?") == [
        "> Previous reported issue.",
        "Could you look at this?",
    ]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"choices": None},
        {"choices": {}},
        {"choices": []},
        {"choices": [None]},
        {"choices": ["bad"]},
        {"choices": [{"finish_reason": "stop", "message": None}]},
        {"choices": [{"finish_reason": "stop", "message": []}]},
    ],
)
def test_malformed_model_envelopes_record_failed_coverage(
    raw, settings, monkeypatch, payload
):
    mock_model(monkeypatch, settings, completion_payload=payload)
    snapshot = normalize_snapshot(raw)
    result = run_analysis(snapshot, "model", settings)
    assert not result.complete
    assert result.coverage[0].status == "failed"
    assert result.coverage[0].comments_processed == 0
    assert result.cards == []
    assert result.warnings
    assert snapshot.prs[0].comments[0].body == raw["prs"][0]["comments"][0]["body"]
