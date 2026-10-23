"""Source selection cannot invent text or silently crop long discussions."""

import re

import pytest

from reviewradar.model import ModelFailure, ModelOutput, bind_passages, source_passages
from reviewradar.schemas import normalize_snapshot


@pytest.mark.parametrize(
    "body",
    [
        "First request. Also explain this?\nA later paragraph.",
        "Unicode: café, שלום, 👋.\r\nAnd `opts.normalize=True` stays intact.",
        "unbroken" * 200,
        "  " + "word " * 1000 + "\n\nLast sentence.",
        "",
    ],
)
def test_passages_preserve_all_nonwhitespace_text_with_exact_source_spans(body):
    passages = source_passages(body)
    assert all(part and len(part) <= 600 and part in body for part in passages)
    assert re.sub(r"\s", "", "".join(passages)) == re.sub(r"\s", "", body)


def test_invalid_passage_selection_never_falls_back_to_another_source():
    snapshot = normalize_snapshot(
        {
            "schema_version": 1,
            "source": "synthetic",
            "owner": "author",
            "fetched_at": "2026-10-23T10:00:00Z",
            "complete": True,
            "warnings": [],
            "prs": [
                {
                    "id": "example/repo#1",
                    "url": "https://github.com/example/repo/pull/1",
                    "title": "Synthetic",
                    "author": "author",
                    "state": "OPEN",
                    "head_sha": None,
                    "fetched_at": "2026-10-23T10:00:00Z",
                    "complete": True,
                    "warnings": [],
                    "comments": [
                        {
                            "id": "r1",
                            "url": "https://github.com/example/repo/pull/1#issuecomment-1",
                            "author": "reviewer",
                            "is_bot": False,
                            "kind": "comment",
                            "body": "Please add a test.",
                            "created_at": "2026-10-23T09:00:00Z",
                            "updated_at": "2026-10-23T09:00:00Z",
                        }
                    ],
                }
            ],
        }
    )
    fields = {
        "request_passage": "r1/p99",
        "category": "change",
        "rationale": "A test request.",
        "uncertainty": ["Implementation not verified"],
    }
    with pytest.raises(ModelFailure, match="unknown source passage"):
        bind_passages(ModelOutput.model_validate({"cards": [fields]}), snapshot.prs[0])


def test_referential_followup_keeps_original_context_without_merging_distinct_asks():
    body = "Normalization is ignored. Could you take a look at this?"
    assert source_passages(body) == [body]
    assert source_passages("Please add a test. Also explain the fallback.") == [
        "Please add a test.",
        "Also explain the fallback.",
    ]


def test_quoted_context_cannot_be_selected_as_a_new_request():
    from reviewradar.model import ModelOutput, constrained_schema, quoted_only
    from pathlib import Path
    import json

    path = (
        Path(__file__).resolve().parents[1] / "fixtures/public/historical-sample.json"
    )
    raw = json.loads(path.read_text())
    raw["prs"][0]["comments"][0]["body"] = (
        "> Please add a test.\n\nI agree with the original review."
    )
    pr = normalize_snapshot(raw).prs[0]
    schema = constrained_schema(ModelOutput, pr)
    allowed = schema["$defs"]["SpanCandidate"]["properties"]["request_passage"]["enum"]
    assert quoted_only("> Please add a test.")
    assert not quoted_only("Please add a test.")
    assert f"{pr.comments[0].id}/p0" not in allowed
    assert f"{pr.comments[0].id}/p1" in allowed
