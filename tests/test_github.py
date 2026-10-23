"""Bounded intake behavior; mocked gh transport, no network in unit tests."""

import copy
import unittest
from unittest.mock import patch

from backend.reviewradar.github import fetch_github_snapshot, _run_gh

URL = "https://github.com/example/project/pull/12"
OWNER = "contributor"
NOW = "2026-10-23T11:00:00Z"


def node(i=1, *, kind="comment", body="Please add a regression test.", author=None):
    anchor = {
        "comment": "issuecomment-",
        "review": "pullrequestreview-",
        "inline": "discussion_r",
    }[kind]
    n = {
        "id": f"N{i}",
        "databaseId": i,
        "url": f"{URL}#{anchor}{i}",
        "body": body,
        "createdAt": NOW,
        "updatedAt": NOW,
        "author": author or {"login": "reviewer", "__typename": "User"},
    }
    if kind == "review":
        n.update(submittedAt=NOW, state="CHANGES_REQUESTED")
    return n


def connection(nodes=None, more=False, cursor=None):
    return {
        "nodes": nodes or [],
        "pageInfo": {"hasNextPage": more, "endCursor": cursor},
    }


class Transport:
    def __init__(self):
        self.calls = []
        self.meta = {
            "id": "PR12",
            "url": URL,
            "title": "Bounded test",
            "state": "OPEN",
            "merged": False,
            "headRefOid": "a" * 40,
            "author": {"login": OWNER, "__typename": "User"},
        }
        self.private = False
        self.comments = [connection()]
        self.reviews = [connection()]
        self.threads = [connection()]
        self.nested = []
        self.fail = None

    def __call__(self, args, timeout):
        self.calls.append((args, timeout))
        query = next(a[6:] for a in args if a.startswith("query="))
        if "isPrivate" in query:
            return {
                "data": {
                    "repository": {
                        "isPrivate": self.private,
                        "pullRequest": copy.deepcopy(self.meta),
                    }
                }
            }
        if "node(id:$thread)" in query:
            return {"data": {"node": {"comments": self.nested.pop(0)}}}
        field, pages = (
            ("reviewThreads", self.threads)
            if "reviewThreads(" in query
            else (
                ("reviews", self.reviews)
                if "reviews(" in query
                else ("comments", self.comments)
            )
        )
        if field == self.fail:
            return {"errors": [{"message": "unavailable"}], "data": None}
        return {"data": {"repository": {"pullRequest": {field: pages.pop(0)}}}}


class IntakeTests(unittest.TestCase):
    def test_reads_all_three_source_types_and_thread_state(self):
        t = Transport()
        t.comments = [connection([node(1)])]
        t.reviews = [connection([node(2, kind="review", body="")])]
        t.threads = [
            connection(
                [
                    {
                        "id": "T",
                        "isResolved": True,
                        "isOutdated": False,
                        "comments": connection([node(3, kind="inline")]),
                    }
                ]
            )
        ]
        s = fetch_github_snapshot([URL], OWNER, runner=t)
        self.assertTrue(s["complete"])
        self.assertEqual(
            {c["kind"] for c in s["prs"][0]["comments"]},
            {"comment", "review", "inline"},
        )
        self.assertEqual(
            next(c for c in s["prs"][0]["comments"] if c["kind"] == "review")[
                "review_state"
            ],
            "CHANGES_REQUESTED",
        )
        inline = next(c for c in s["prs"][0]["comments"] if c["kind"] == "inline")
        self.assertEqual(
            (inline["thread_id"], inline["thread_resolved"], inline["thread_outdated"]),
            ("T", True, False),
        )
        for args, timeout in t.calls:
            self.assertEqual(args[:3], ["gh", "api", "graphql"])
            self.assertGreater(timeout, 0)
            self.assertLessEqual(timeout, 60)
            self.assertFalse(any("mutation" in a for a in args))

    def test_top_level_and_nested_pagination(self):
        t = Transport()
        t.comments = [connection([node(1)], True, "C1"), connection([node(2)])]
        t.threads = [
            connection(
                [
                    {
                        "id": "T",
                        "isResolved": False,
                        "isOutdated": True,
                        "comments": connection([node(3, kind="inline")], True, "T1"),
                    }
                ]
            )
        ]
        t.nested = [connection([node(4, kind="inline")])]
        s = fetch_github_snapshot([URL], OWNER, runner=t)
        self.assertTrue(s["complete"])
        self.assertEqual(len(s["prs"][0]["comments"]), 4)
        self.assertTrue(any("cursor=C1" in args for args, _ in t.calls))
        self.assertTrue(any("cursor=T1" in args for args, _ in t.calls))

    def test_input_casing_retains_github_canonical_identity(self):
        t = Transport()
        s = fetch_github_snapshot(
            [URL.replace("example/project", "EXAMPLE/PROJECT")], OWNER.upper(), runner=t
        )
        self.assertEqual(s["prs"][0]["id"], "example/project#12")
        self.assertEqual(s["prs"][0]["url"], URL)

    def test_wrong_author_or_private_refused_before_body(self):
        for private in [True, False]:
            with self.subTest(private=private):
                t = Transport()
                t.private = private
                if not private:
                    t.meta["author"]["login"] = "someoneelse"
                with self.assertRaises(ValueError):
                    fetch_github_snapshot([URL], OWNER, runner=t)
                self.assertEqual(len(t.calls), 1)

    def test_unsafe_or_duplicate_urls_never_execute(self):
        for urls in [
            ["https://evil.test/a"],
            [URL + "?x=1"],
            [URL + "#a"],
            [URL, URL],
            [URL.replace("/project/", "/../")],
            [],
        ]:
            with self.subTest(urls=urls):
                t = Transport()
                with self.assertRaises(ValueError):
                    fetch_github_snapshot(urls, OWNER, runner=t)
                self.assertEqual(t.calls, [])

    def test_query_failure_marks_partial_not_clean(self):
        t = Transport()
        t.fail = "reviews"
        s = fetch_github_snapshot([URL], OWNER, runner=t)
        self.assertFalse(s["complete"])
        self.assertFalse(s["prs"][0]["complete"])
        self.assertIn("reviews coverage incomplete", s["prs"][0]["warnings"][0])

    def test_body_limit_omits_without_cropping_and_warns(self):
        t = Transport()
        t.comments = [
            connection([node(1, body="a" * 20_001), node(2, body="untouched")])
        ]
        s = fetch_github_snapshot([URL], OWNER, runner=t)
        self.assertFalse(s["complete"])
        self.assertEqual([c["body"] for c in s["prs"][0]["comments"]], ["untouched"])
        self.assertIn("not truncated", s["prs"][0]["warnings"][0])

    def test_200_record_limit_visible(self):
        t = Transport()
        t.comments = [
            connection([node(i) for i in range(100)], True, "A"),
            connection([node(i) for i in range(100, 200)], True, "B"),
            connection([node(201)]),
        ]
        s = fetch_github_snapshot([URL], OWNER, runner=t)
        self.assertFalse(s["complete"])
        self.assertEqual(len(s["prs"][0]["comments"]), 200)
        self.assertTrue(any("200-source" in w for w in s["prs"][0]["warnings"]))

    def test_missing_or_repeated_cursor_visible(self):
        t = Transport()
        t.comments = [connection([node(1)], True, None)]
        s = fetch_github_snapshot([URL], OWNER, runner=t)
        self.assertFalse(s["complete"])
        self.assertIn("cursor", s["prs"][0]["warnings"][0])

    def test_deleted_actor_and_bots_preserved(self):
        t = Transport()
        deleted = node(1)
        deleted["author"] = None
        t.comments = [
            connection(
                [
                    deleted,
                    node(2, author={"login": "github-actions", "__typename": "Bot"}),
                ]
            )
        ]
        s = fetch_github_snapshot([URL], OWNER, runner=t)
        self.assertEqual(s["prs"][0]["comments"][0]["author"], "[deleted]")
        self.assertTrue(s["prs"][0]["comments"][1]["is_bot"])
        self.assertFalse(s["complete"])

    def test_single_deadline_stops_later_reads_and_preserves_partial(self):
        t = Transport()
        # Import starts at 0; metadata gets remaining 59s; body reads exceed the same deadline.
        with patch(
            "backend.reviewradar.github.time.monotonic",
            side_effect=[0.0, 1.0, 61.0, 62.0, 63.0],
        ):
            s = fetch_github_snapshot([URL], OWNER, runner=t)
        self.assertFalse(s["complete"])
        self.assertEqual(len(t.calls), 1)
        self.assertTrue(all("budget" in w for w in s["prs"][0]["warnings"]))

    def test_foreign_source_link_is_omitted_with_warning(self):
        t = Transport()
        bad = node(1)
        bad["url"] = URL + "#issuecomment-1bad"
        t.comments = [connection([bad])]
        s = fetch_github_snapshot([URL], OWNER, runner=t)
        self.assertFalse(s["complete"])
        self.assertEqual(s["prs"][0]["comments"], [])
        self.assertIn("unexpected source URL", s["prs"][0]["warnings"][0])

    def test_subprocess_is_array_readonly_no_shell(self):
        from types import SimpleNamespace

        with patch(
            "backend.reviewradar.github.subprocess.run",
            return_value=SimpleNamespace(returncode=0, stdout='{"data":{}}'),
        ) as run:
            _run_gh(["gh", "api", "graphql", "-f", "query=query{viewer{login}}"], 2.0)
            args, kwargs = run.call_args
            self.assertIsInstance(args[0], list)
            self.assertNotIn("shell", kwargs)
            self.assertEqual(kwargs["timeout"], 2.0)

    def test_unknown_pagination_never_claims_complete_coverage(self):
        for info in [
            {},
            {"hasNextPage": None},
            {"hasNextPage": "false"},
            {"hasNextPage": 0},
        ]:
            for nested in [False, True]:
                with self.subTest(info=info, nested=nested):
                    t = Transport()
                    malformed = {
                        "nodes": [node(1, kind="inline" if nested else "comment")],
                        "pageInfo": info,
                    }
                    if nested:
                        t.threads = [
                            connection(
                                [
                                    {
                                        "id": "T",
                                        "isResolved": False,
                                        "isOutdated": False,
                                        "comments": malformed,
                                    }
                                ]
                            )
                        ]
                    else:
                        t.comments = [malformed]
                    s = fetch_github_snapshot([URL], OWNER, runner=t)
                    self.assertFalse(s["complete"])
                    self.assertTrue(
                        any("pagination" in w for w in s["prs"][0]["warnings"])
                    )

    def test_malformed_nodes_are_omitted_but_valid_sources_survive(self):
        for malformed in [
            None,
            [],
            "bad node",
            {**node(1), "author": ["bad"]},
            {**node(1), "author": {"login": 9}},
            {**node(1), "createdAt": "not a date"},
        ]:
            with self.subTest(malformed=malformed):
                t = Transport()
                t.comments = [connection([malformed, node(2)])]
                s = fetch_github_snapshot([URL], OWNER, runner=t)
                self.assertFalse(s["complete"])
                self.assertEqual(
                    [c["id"] for c in s["prs"][0]["comments"]], ["comment:2"]
                )
                self.assertTrue(s["prs"][0]["warnings"])

    def test_malformed_connections_and_threads_preserve_partial_intake(self):
        for malformed in [
            None,
            [],
            {"nodes": None, "pageInfo": {"hasNextPage": False}},
        ]:
            with self.subTest(connection=malformed):
                t = Transport()
                t.comments = [malformed]
                t.reviews = [connection([node(2, kind="review")])]
                s = fetch_github_snapshot([URL], OWNER, runner=t)
                self.assertFalse(s["complete"])
                self.assertEqual(
                    [c["id"] for c in s["prs"][0]["comments"]], ["review:2"]
                )
        t = Transport()
        t.comments = [connection([node(1)])]
        t.threads = [connection([None])]
        s = fetch_github_snapshot([URL], OWNER, runner=t)
        self.assertFalse(s["complete"])
        self.assertEqual([c["id"] for c in s["prs"][0]["comments"]], ["comment:1"])

    def test_malformed_metadata_is_rejected_before_bodies(self):
        for fields in [{"author": ["bad"]}, {"title": None}, {"state": []}]:
            with self.subTest(fields=fields):
                t = Transport()
                t.meta.update(fields)
                with self.assertRaises(ValueError):
                    fetch_github_snapshot([URL], OWNER, runner=t)
                self.assertEqual(len(t.calls), 1)


if __name__ == "__main__":
    unittest.main()
