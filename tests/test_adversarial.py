"""Independent behavioral security/reliability audit; never calls real inference."""

import asyncio
from pathlib import Path
import tempfile
import unittest

import httpx
from fastapi.testclient import TestClient

from backend.reviewradar.analysis import (
    export_markdown,
    run_analysis,
    validate_candidates,
)
from backend.reviewradar.app import create_app
from backend.reviewradar.config import MAX_BODY_BYTES, Settings
from backend.reviewradar.model import Candidate, ModelFailure
from backend.reviewradar.schemas import normalize_snapshot
from backend.reviewradar.store import Store

URL = "https://github.com/example/project/pull/10"
BASE = "http://127.0.0.1:8893"


def raw_snapshot():
    return {
        "schema_version": 1,
        "fetched_at": "2026-10-23T12:00:00Z",
        "source": "synthetic",
        "owner": "owner",
        "complete": True,
        "warnings": [],
        "prs": [
            {
                "id": "example/project#10",
                "url": URL,
                "title": "Synthetic adversarial fixture",
                "author": "owner",
                "state": "OPEN",
                "head_sha": "a" * 40,
                "fetched_at": "2026-10-23T12:00:00Z",
                "complete": True,
                "warnings": [],
                "comments": [
                    {
                        "id": "r1",
                        "url": URL + "#issuecomment-1",
                        "author": "reviewer",
                        "is_bot": False,
                        "kind": "comment",
                        "body": "Please add the test. <script>alert(1)</script>",
                        "created_at": "2026-10-23T10:00:00Z",
                        "updated_at": "2026-10-23T10:00:00Z",
                        "review_state": None,
                        "thread_id": None,
                        "thread_resolved": None,
                        "thread_outdated": None,
                    },
                    {
                        "id": "a1",
                        "url": URL + "#issuecomment-2",
                        "author": "owner",
                        "is_bot": False,
                        "kind": "comment",
                        "body": "Added the test; inspect it.",
                        "created_at": "2026-10-23T11:00:00Z",
                        "updated_at": "2026-10-23T11:00:00Z",
                        "review_state": None,
                        "thread_id": None,
                        "thread_resolved": None,
                        "thread_outdated": None,
                    },
                ],
            }
        ],
    }


def candidate(**changes):
    fields = {
        "request_id": "r1",
        "request_quote": "Please add the test.",
        "response_id": "a1",
        "response_quote": "Added the test",
        "category": "change",
        "interpretation": "possibly_responded",
        "rationale": "Possible conversational response; implementation not verified.",
        "uncertainty": ["Not a code verifier"],
    }
    fields.update(changes)
    return Candidate(**fields)


class AdversarialAPITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.settings = Settings(data_dir=Path(self.temp.name), api_token="a" * 40)
        self.app = create_app(self.settings)
        self.client = TestClient(self.app, base_url=BASE)
        self.headers = {"X-ReviewRadar-Token": "a" * 40, "Origin": BASE}

    def tearDown(self):
        self.client.close()
        self.temp.cleanup()

    def test_host_and_origin_boundaries_protect_bootstrap(self):
        for url, headers, expected in [
            ("/runtime-config", {"Host": "attacker.test:8893"}, 400),
            ("/runtime-config", {"Origin": "https://attacker.test"}, 403),
            ("/runtime-config", {"Sec-Fetch-Site": "cross-site"}, 403),
            ("/api/health", {"Origin": "null"}, 403),
            ("/api/snapshots", {}, 401),
            ("/api/snapshots", {"X-ReviewRadar-Token": "expired"}, 401),
        ]:
            with self.subTest(url=url, headers=headers):
                response = self.client.get(url, headers=headers)
                self.assertEqual(response.status_code, expected)
                self.assertNotIn('"api_token"', response.text)
        response = self.client.get("/runtime-config")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(response.headers["x-content-type-options"], "nosniff")

    def test_mutation_requires_origin_and_json(self):
        no_origin = self.client.post(
            "/api/snapshots/import",
            json={"snapshot": raw_snapshot()},
            headers={"X-ReviewRadar-Token": "a" * 40},
        )
        self.assertEqual(no_origin.status_code, 403)
        wrong_type = self.client.post(
            "/api/snapshots/import", content="{}", headers=self.headers
        )
        self.assertEqual(wrong_type.status_code, 415)

    def test_advertised_and_chunked_body_limits(self):
        response = self.client.post(
            "/api/snapshots/import",
            content="{}",
            headers={
                **self.headers,
                "Content-Type": "application/json",
                "Content-Length": str(MAX_BODY_BYTES + 1),
            },
        )
        self.assertEqual(response.status_code, 413)

        async def run():
            async def chunks():
                yield b" " * MAX_BODY_BYTES
                yield b" "

            transport = httpx.ASGITransport(app=self.app)
            async with httpx.AsyncClient(transport=transport, base_url=BASE) as client:
                return await client.post(
                    "/api/snapshots/import",
                    content=chunks(),
                    headers={**self.headers, "Content-Type": "application/json"},
                )

        self.assertEqual(asyncio.run(run()).status_code, 413)

    def test_import_does_not_trust_supplied_hash_or_foreign_source(self):
        raw = raw_snapshot()
        raw["id"] = "f" * 64
        response = self.client.post(
            "/api/snapshots/import", json={"snapshot": raw}, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.json()["id"], "f" * 64)
        raw["prs"][0]["comments"][0]["url"] = "https://evil.test/#issuecomment-1"
        bad = self.client.post(
            "/api/snapshots/import", json={"snapshot": raw}, headers=self.headers
        )
        self.assertEqual(bad.status_code, 422)
        self.assertNotIn("Please add", bad.text)
        self.assertEqual(
            len(self.client.get("/api/snapshots", headers=self.headers).json()), 1
        )

    def test_decisions_are_reversible_and_bound_to_analysis_card(self):
        imported = self.client.post(
            "/api/snapshots/import",
            json={"snapshot": raw_snapshot()},
            headers=self.headers,
        ).json()
        one = self.client.post(
            "/api/analyses",
            json={"snapshot_id": imported["id"], "mode": "baseline"},
            headers=self.headers,
        ).json()
        two = self.client.post(
            "/api/analyses",
            json={"snapshot_id": imported["id"], "mode": "baseline"},
            headers=self.headers,
        ).json()
        path = f"/api/analyses/{one['id']}/cards/{one['cards'][0]['id']}/disposition"
        self.assertEqual(
            self.client.put(
                path, json={"state": "reviewed", "note": "test"}, headers=self.headers
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(
                f"/api/analyses/{two['id']}/dispositions", headers=self.headers
            ).json(),
            [],
        )
        self.assertEqual(
            self.client.put(
                path, json={"state": "open", "note": ""}, headers=self.headers
            ).json()["state"],
            "open",
        )
        wrong = self.client.put(
            path.replace(one["cards"][0]["id"], "missing"),
            json={"state": "reviewed", "note": ""},
            headers=self.headers,
        )
        self.assertEqual(wrong.status_code, 404)
        self.assertEqual(
            self.client.get(
                f"/api/snapshots/{imported['id']}", headers=self.headers
            ).json(),
            imported,
        )


class EvidenceBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.settings = Settings(data_dir=Path(self.temp.name))

    def tearDown(self):
        self.temp.cleanup()

    def test_temporally_equal_or_other_author_responses_rejected(self):
        for change in ["time", "author"]:
            raw = raw_snapshot()
            response = raw["prs"][0]["comments"][1]
            if change == "time":
                response["created_at"] = raw["prs"][0]["comments"][0]["created_at"]
            else:
                response["author"] = "differentreviewer"
            pr = normalize_snapshot(raw).prs[0]
            with self.assertRaises(ModelFailure):
                validate_candidates([candidate()], pr)

    def test_model_cannot_cite_bot_author_or_unknown_request(self):
        for change in ["bot", "author", "unknown"]:
            raw = raw_snapshot()
            args = {}
            if change == "bot":
                raw["prs"][0]["comments"][0]["is_bot"] = True
            elif change == "author":
                raw["prs"][0]["comments"][0]["author"] = "owner"
            else:
                args["request_id"] = "foreign:1"
            with self.assertRaises(ModelFailure):
                validate_candidates([candidate(**args)], normalize_snapshot(raw).prs[0])

    def test_failed_or_partial_analysis_never_clean(self):
        class FailureModel:
            def analyze(self, _pr):
                raise ModelFailure("Deliberate test timeout")

        full = normalize_snapshot(raw_snapshot())
        failed = run_analysis(full, "model", self.settings, model=FailureModel())
        self.assertFalse(failed.complete)
        self.assertEqual(failed.cards, [])
        self.assertEqual(failed.coverage[0].status, "failed")
        self.assertIn("does not certify", export_markdown(failed, full, []))
        raw = raw_snapshot()
        raw["complete"] = raw["prs"][0]["complete"] = False
        raw["warnings"] = ["Other sources omitted."]
        partial = normalize_snapshot(raw)
        result = run_analysis(partial, "baseline", self.settings)
        self.assertFalse(result.complete)
        self.assertGreater(len(result.cards), 0)
        self.assertIn("incomplete", result.coverage[0].reason)

    def test_store_rejects_identity_reuse_and_reload_preserves_sources(self):
        snapshot = normalize_snapshot(raw_snapshot())
        store = Store(Path(self.temp.name))
        store.save_snapshot(snapshot)
        changed = snapshot.model_copy(deep=True)
        changed.prs[0].comments[0].body = "silently changed"
        with self.assertRaises(ValueError):
            store.save_snapshot(changed)
        self.assertEqual(
            Store(Path(self.temp.name)).get_snapshot(snapshot.id).model_dump(),
            snapshot.model_dump(),
        )

    def test_export_escapes_untrusted_html_and_markdown(self):
        snapshot = normalize_snapshot(raw_snapshot())
        result = run_analysis(snapshot, "baseline", self.settings)
        output = export_markdown(result, snapshot, [])
        self.assertNotIn("<script>", output)
        self.assertIn("\\<script\\>", output)
        self.assertIn(URL + "#issuecomment-1", output)
        self.assertIn("conversational evidence, not verification", output)


if __name__ == "__main__":
    unittest.main()
