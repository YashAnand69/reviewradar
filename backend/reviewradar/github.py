"""Read-only, bounded public GitHub intake. No shell or model-generated queries."""

from __future__ import annotations

import json
import re
import subprocess
import time
from datetime import datetime, timezone
from typing import Any, Callable

from .config import MAX_PRS, MAX_COMMENTS, MAX_COMMENT_CHARS
from .schemas import Comment

MAX_BODY_CHARS = MAX_COMMENT_CHARS
MAX_SECONDS = 60.0
MAX_PAGES = 10
PR_PATTERN = re.compile(
    r"https://github\.com/([A-Za-z0-9](?:[A-Za-z0-9-]{0,38}))/([A-Za-z0-9_.-]{1,100})/pull/([1-9][0-9]{0,8})\Z"
)
OWNER_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}\Z")
Runner = Callable[[list[str], float], dict[str, Any]]

ACTOR = "author { login __typename }"
META_QUERY = """query($owner:String!,$repo:String!,$number:Int!){repository(owner:$owner,name:$repo){isPrivate pullRequest(number:$number){id url title state merged headRefOid author{login __typename}}}}"""
COMMENT_FIELDS = "id databaseId url body createdAt updatedAt " + ACTOR
REVIEW_FIELDS = "id databaseId url body submittedAt updatedAt state " + ACTOR
INLINE_FIELDS = COMMENT_FIELDS
PAGE_INFO = "pageInfo { hasNextPage endCursor }"


def _connection(value: Any) -> dict[str, Any]:
    """Unknown continuation is incomplete coverage, never an empty last page."""
    if not isinstance(value, dict) or not isinstance(value.get("nodes"), list):
        raise ValueError("GitHub returned a malformed paginated connection.")
    info = value.get("pageInfo")
    if not isinstance(info, dict) or type(info.get("hasNextPage")) is not bool:
        raise ValueError(
            "GitHub returned invalid pagination metadata; coverage is incomplete."
        )
    if info["hasNextPage"] and (
        not isinstance(info.get("endCursor"), str) or not info["endCursor"]
    ):
        raise ValueError("GitHub returned a repeated or missing page cursor.")
    return value


def _run_gh(args: list[str], timeout: float) -> dict[str, Any]:
    try:
        result = subprocess.run(
            args, check=False, capture_output=True, text=True, timeout=timeout
        )
    except FileNotFoundError as exc:
        raise ValueError(
            "GitHub CLI is unavailable. Install gh or import a snapshot JSON."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ValueError(
            "GitHub intake exceeded its time budget; retry fewer PRs."
        ) from exc
    if result.returncode:
        # Do not leak credentials, arbitrary stderr or private repository metadata.
        raise ValueError(
            "GitHub could not complete this read. Check gh authentication, public access and rate limits."
        )
    try:
        payload = json.loads(result.stdout)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("GitHub returned an unreadable response.") from exc
    if not isinstance(payload, dict):
        raise ValueError("GitHub returned an unexpected response.")
    return payload


def fetch_github_snapshot(
    urls: list[str], owner: str, *, runner: Runner | None = None
) -> dict[str, Any]:
    """Return v1 raw snapshot without ID; caller validates/hashes before persistence.

    All selected PRs must be public and authored by owner. Input rejection is
    atomic. Read failures after verified metadata yield visible incomplete PRs.
    A single monotonic deadline covers the entire import, not each API call.
    """
    if not isinstance(owner, str) or not OWNER_PATTERN.fullmatch(owner):
        raise ValueError("Enter a valid GitHub handle.")
    if not isinstance(urls, list) or not 1 <= len(urls) <= MAX_PRS:
        raise ValueError(f"Choose one to {MAX_PRS} public authored PR URLs.")
    parsed: list[tuple[str, str, str, int]] = []
    seen_urls: set[str] = set()
    for url in urls:
        match = PR_PATTERN.fullmatch(url) if isinstance(url, str) else None
        if not match or match[2] in {".", ".."}:
            raise ValueError(
                "Use canonical https://github.com/OWNER/REPO/pull/NUMBER URLs without query strings or fragments."
            )
        if url.casefold() in seen_urls:
            raise ValueError("Each selected PR URL must be unique.")
        seen_urls.add(url.casefold())
        parsed.append((url, match[1], match[2], int(match[3])))
    transport = runner or _run_gh
    deadline = time.monotonic() + MAX_SECONDS
    fetched_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def query(document: str, variables: dict[str, Any]) -> dict[str, Any]:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError("The 60-second GitHub intake budget was exhausted.")
        args = ["gh", "api", "graphql", "-f", f"query={document}"]
        for key, value in variables.items():
            if value is None:
                continue
            args.extend(["-F" if isinstance(value, int) else "-f", f"{key}={value}"])
        payload = transport(args, remaining)
        if (
            not isinstance(payload, dict)
            or payload.get("errors")
            or not isinstance(payload.get("data"), dict)
        ):
            raise ValueError("GitHub reported a query failure; coverage is incomplete.")
        return payload["data"]

    # Verify visibility and ownership for every selected PR before taking bodies.
    verified = []
    for input_url, repo_owner, repo, number in parsed:
        variables = {"owner": repo_owner, "repo": repo, "number": number}
        data = query(META_QUERY, variables)
        repository = data.get("repository")
        if not isinstance(repository, dict) or repository.get("isPrivate") is not False:
            raise ValueError("Only accessible public repositories are supported.")
        pr = repository.get("pullRequest")
        author = pr.get("author") if isinstance(pr, dict) else None
        if (
            not isinstance(pr, dict)
            or not isinstance(author, dict)
            or not isinstance(author.get("login"), str)
            or author["login"].casefold() != owner.casefold()
        ):
            raise ValueError(
                "Every selected PR must be authored by the supplied GitHub handle."
            )
        if str(pr.get("url", "")).casefold() != input_url.casefold():
            raise ValueError(
                "GitHub returned a different PR URL; use its canonical public URL."
            )
        if (
            not isinstance(pr.get("title"), str)
            or not isinstance(pr.get("state"), str)
            or pr.get("state") not in {"OPEN", "CLOSED", "MERGED"}
            or type(pr.get("merged")) is not bool
            or (
                pr.get("headRefOid") is not None
                and not isinstance(pr["headRefOid"], str)
            )
        ):
            raise ValueError("GitHub returned malformed pull request metadata.")
        verified.append((pr, variables))

    prs = []
    for metadata, variables in verified:
        pr_url = metadata["url"]
        canonical = PR_PATTERN.fullmatch(pr_url)
        if canonical is None:
            raise ValueError("GitHub returned an invalid canonical PR URL.")
        pr_id = f"{canonical[1]}/{canonical[2]}#{canonical[3]}"
        warnings: list[str] = []
        comments: dict[str, dict[str, Any]] = {}
        capped = False

        def add(
            node: dict[str, Any], kind: str, thread: dict[str, Any] | None = None
        ) -> None:
            nonlocal capped
            if not isinstance(node, dict):
                warnings.append(f"A {kind} source was malformed and was omitted.")
                return
            prefix = {"comment": "comment", "review": "review", "inline": "inline"}[
                kind
            ]
            identity = node.get("databaseId") or node.get("id")
            if not identity:
                warnings.append(
                    f"A {kind} source had no stable identity and was omitted."
                )
                return
            source_id = f"{prefix}:{identity}"
            if source_id in comments:
                return
            if len(comments) >= MAX_COMMENTS:
                capped = True
                return
            body = node.get("body")
            if not isinstance(body, str):
                warnings.append(
                    f"A {kind} source had no readable original body and was omitted."
                )
                return
            if len(body) > MAX_BODY_CHARS:
                warnings.append(
                    f"{source_id} exceeded the {MAX_BODY_CHARS}-character body limit and was omitted, not truncated."
                )
                return
            url = node.get("url", "")
            expected_anchor = {
                "comment": "issuecomment-",
                "review": "pullrequestreview-",
                "inline": "discussion_r",
            }[kind]
            if not isinstance(url, str) or not re.fullmatch(
                re.escape(pr_url + "#" + expected_anchor) + r"[0-9]+", url
            ):
                warnings.append(
                    f"{source_id} had an unexpected source URL and was omitted."
                )
                return
            actor = node.get("author") or {}
            if not isinstance(actor, dict):
                warnings.append(
                    f"{source_id} had malformed author metadata and was omitted."
                )
                return
            actor_name = actor.get("login") or "[deleted]"
            if not isinstance(actor_name, str):
                warnings.append(
                    f"{source_id} had malformed author metadata and was omitted."
                )
                return
            if actor_name == "[deleted]":
                warnings.append(f"{source_id} has a deleted or unavailable author.")
            created = (
                node.get("submittedAt") if kind == "review" else node.get("createdAt")
            )
            updated = node.get("updatedAt") or created
            if not created or not updated:
                warnings.append(f"{source_id} lacked a timestamp and was omitted.")
                return
            source = {
                "id": source_id,
                "url": url,
                "author": actor_name,
                "is_bot": actor.get("__typename") == "Bot"
                or actor_name.endswith("[bot]"),
                "kind": kind,
                "body": body,
                "created_at": created,
                "updated_at": updated,
                "review_state": node.get("state") if kind == "review" else None,
                "thread_id": thread.get("id") if thread else None,
                "thread_resolved": thread.get("isResolved") if thread else None,
                "thread_outdated": thread.get("isOutdated") if thread else None,
            }
            try:
                comments[source_id] = Comment.model_validate(source).model_dump()
            except ValueError:
                warnings.append(
                    f"{source_id} had invalid source metadata and was omitted."
                )

        def page_connection(field: str, fields: str):
            cursor = None
            cursors: set[str] = set()
            for _ in range(MAX_PAGES):
                document = f"query($owner:String!,$repo:String!,$number:Int!,$cursor:String){{repository(owner:$owner,name:$repo){{pullRequest(number:$number){{{field}(first:100,after:$cursor){{nodes{{{fields}}} {PAGE_INFO}}}}}}}}}"
                data = query(document, {**variables, "cursor": cursor})
                connection = _connection(data["repository"]["pullRequest"][field])
                yield connection["nodes"]
                info = connection["pageInfo"]
                if not info["hasNextPage"]:
                    return
                cursor = info.get("endCursor")
                if not cursor or cursor in cursors:
                    raise ValueError(
                        "GitHub returned a repeated or missing page cursor."
                    )
                cursors.add(cursor)
                if capped:
                    return
            raise ValueError("The pagination safety limit was reached.")

        for field, fields, kind in [
            ("comments", COMMENT_FIELDS, "comment"),
            ("reviews", REVIEW_FIELDS, "review"),
        ]:
            try:
                for nodes in page_connection(field, fields):
                    for node in nodes:
                        add(node, kind)
                    if capped:
                        break
            except (ValueError, KeyError, TypeError) as exc:
                warnings.append(
                    f"{field} coverage incomplete: {str(exc) if isinstance(exc, ValueError) else 'unexpected GitHub data shape'}"
                )

        thread_fields = f"id isResolved isOutdated comments(first:100){{nodes{{{INLINE_FIELDS}}} {PAGE_INFO}}}"
        try:
            for threads in page_connection("reviewThreads", thread_fields):
                for thread in threads:
                    if (
                        not isinstance(thread, dict)
                        or not isinstance(thread.get("id"), str)
                        or type(thread.get("isResolved")) is not bool
                        or type(thread.get("isOutdated")) is not bool
                    ):
                        raise ValueError(
                            "GitHub returned malformed inline thread metadata."
                        )
                    connection = _connection(thread["comments"])
                    nested_cursors: set[str] = set()
                    for _ in range(MAX_PAGES):
                        for node in connection["nodes"]:
                            add(node, "inline", thread)
                        info = connection["pageInfo"]
                        if not info["hasNextPage"] or capped:
                            break
                        cursor = info.get("endCursor")
                        if not cursor or cursor in nested_cursors:
                            raise ValueError(
                                "GitHub returned a repeated nested thread cursor."
                            )
                        nested_cursors.add(cursor)
                        document = f"query($thread:ID!,$cursor:String){{node(id:$thread){{... on PullRequestReviewThread{{comments(first:100,after:$cursor){{nodes{{{INLINE_FIELDS}}} {PAGE_INFO}}}}}}}}}"
                        connection = _connection(
                            query(document, {"thread": thread["id"], "cursor": cursor})[
                                "node"
                            ]["comments"]
                        )
                    else:
                        raise ValueError(
                            "The nested thread pagination safety limit was reached."
                        )
                    if capped:
                        break
                if capped:
                    break
        except (ValueError, KeyError, TypeError) as exc:
            warnings.append(
                f"inline thread coverage incomplete: {str(exc) if isinstance(exc, ValueError) else 'unexpected GitHub data shape'}"
            )
        if capped:
            warnings.append(
                f"The {MAX_COMMENTS}-source per-PR limit was reached; additional sources were omitted."
            )
        unique_warnings = list(dict.fromkeys(warnings))
        if len(unique_warnings) > 50:
            unique_warnings = unique_warnings[:49] + [
                f"{len(unique_warnings) - 49} additional intake warnings omitted; source coverage remains incomplete."
            ]
        prs.append(
            {
                "id": pr_id,
                "url": pr_url,
                "title": metadata["title"],
                "author": metadata["author"]["login"],
                "state": "MERGED" if metadata.get("merged") else metadata["state"],
                "head_sha": metadata.get("headRefOid"),
                "fetched_at": fetched_at,
                "complete": not warnings,
                "warnings": unique_warnings,
                "comments": sorted(
                    comments.values(), key=lambda c: (c["created_at"], c["id"])
                ),
            }
        )
    all_complete = all(pr["complete"] for pr in prs)
    return {
        "schema_version": 1,
        "fetched_at": fetched_at,
        "source": "github",
        "owner": owner,
        "prs": prs,
        "complete": all_complete,
        "warnings": []
        if all_complete
        else [
            "One or more PRs have incomplete source coverage. Inspect per-PR warnings."
        ],
    }
