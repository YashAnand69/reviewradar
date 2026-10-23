"""Wire schemas and the immutable source-evidence boundary."""

from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .config import MAX_COMMENTS, MAX_COMMENT_CHARS, MAX_PRS, MAX_QUOTE_CHARS


LOGIN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?\Z")
PR_PATH = re.compile(r"/([A-Za-z0-9-]+)/([A-Za-z0-9_.-]+)/pull/([1-9][0-9]{0,8})\Z")
ANCHOR = re.compile(
    r"(?:issuecomment-[0-9]+|pullrequestreview-[0-9]+|discussion_r[0-9]+)\Z"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def timestamp(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("Timestamp must be an ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError("Timestamp must include its timezone")
    return parsed


def parse_pr_url(value: str) -> tuple[str, str, int]:
    if not isinstance(value, str) or len(value) > 300:
        raise ValueError("Expected a canonical public GitHub pull request URL")
    parsed = urlsplit(value)
    match = PR_PATH.fullmatch(parsed.path)
    if (
        parsed.scheme != "https"
        or parsed.netloc != "github.com"
        or parsed.query
        or parsed.fragment
        or not match
    ):
        raise ValueError(
            "Use https://github.com/OWNER/REPO/pull/NUMBER without query, fragment or extra path"
        )
    return match.group(1), match.group(2), int(match.group(3))


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Comment(StrictModel):
    id: str = Field(min_length=1, max_length=200)
    url: str = Field(max_length=400)
    author: str = Field(min_length=1, max_length=100)
    is_bot: bool
    kind: Literal["comment", "review", "inline"]
    body: str = Field(max_length=MAX_COMMENT_CHARS)
    created_at: str
    updated_at: str
    review_state: str | None = Field(default=None, max_length=40)
    thread_id: str | None = Field(default=None, max_length=200)
    thread_resolved: bool | None = None
    thread_outdated: bool | None = None

    @field_validator("created_at", "updated_at")
    @classmethod
    def dates(cls, value: str) -> str:
        timestamp(value)
        return value

    @model_validator(mode="after")
    def consistent(self) -> "Comment":
        if timestamp(self.updated_at) < timestamp(self.created_at):
            raise ValueError("Comment update predates creation")
        if self.author.casefold().endswith("[bot]"):
            self.is_bot = True
        return self


class PR(StrictModel):
    id: str = Field(min_length=1, max_length=200)
    url: str
    title: str = Field(max_length=500)
    author: str = Field(min_length=1, max_length=100)
    state: Literal["OPEN", "CLOSED", "MERGED"]
    head_sha: str | None = Field(default=None, max_length=64)
    fetched_at: str
    complete: bool
    warnings: list[str] = Field(default_factory=list, max_length=50)
    comments: list[Comment] = Field(max_length=MAX_COMMENTS)

    @field_validator("fetched_at")
    @classmethod
    def dates(cls, value: str) -> str:
        timestamp(value)
        return value

    @model_validator(mode="after")
    def source_namespace(self) -> "PR":
        owner, repo, number = parse_pr_url(self.url)
        if self.id != f"{owner}/{repo}#{number}":
            raise ValueError("PR ID does not match its canonical URL")
        seen: set[str] = set()
        for comment in self.comments:
            parsed = urlsplit(comment.url)
            if (
                parsed.scheme != "https"
                or parsed.netloc != "github.com"
                or parsed.path != f"/{owner}/{repo}/pull/{number}"
                or parsed.query
                or not ANCHOR.fullmatch(parsed.fragment)
            ):
                raise ValueError(
                    "Comment URL must identify a comment in the same GitHub pull request"
                )
            if comment.id in seen:
                raise ValueError("Duplicate source comment ID")
            seen.add(comment.id)
        self.comments.sort(key=lambda c: (timestamp(c.created_at), c.id))
        return self


class Snapshot(StrictModel):
    schema_version: Literal[1] = 1
    id: str = Field(pattern=r"^[a-f0-9]{64}$")
    fetched_at: str
    source: Literal["github", "import", "synthetic"]
    owner: str = Field(min_length=1, max_length=39)
    prs: list[PR] = Field(min_length=1, max_length=MAX_PRS)
    complete: bool
    warnings: list[str] = Field(default_factory=list, max_length=50)

    @field_validator("fetched_at")
    @classmethod
    def dates(cls, value: str) -> str:
        timestamp(value)
        return value

    @field_validator("owner")
    @classmethod
    def login(cls, value: str) -> str:
        if not LOGIN.fullmatch(value):
            raise ValueError("Use a valid GitHub login")
        return value

    @model_validator(mode="after")
    def ownership(self) -> "Snapshot":
        if len({pr.id for pr in self.prs}) != len(self.prs):
            raise ValueError("Duplicate PRs in snapshot")
        for pr in self.prs:
            if pr.author.casefold() != self.owner.casefold():
                raise ValueError(
                    "Every PR must be authored by the selected GitHub login"
                )
        self.complete = self.complete and all(pr.complete for pr in self.prs)
        return self


def normalize_snapshot(data: dict, *, source: str | None = None) -> Snapshot:
    candidate = dict(data)
    candidate["id"] = "0" * 64
    if source is not None:
        candidate["source"] = source
    result = Snapshot.model_validate(candidate)
    payload = result.model_dump(exclude={"id"})
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    result.id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return result


class Evidence(StrictModel):
    comment_id: str = Field(min_length=1, max_length=200)
    quote: str = Field(min_length=1, max_length=MAX_QUOTE_CHARS)


class GitHubState(StrictModel):
    review_state: str | None = None
    thread_resolved: bool | None = None
    thread_outdated: bool | None = None


class Card(StrictModel):
    id: str = Field(min_length=1, max_length=100)
    pr_id: str
    request: Evidence
    response: Evidence | None = None
    category: Literal["change", "question", "suggestion", "unclear"]
    interpretation: Literal["follow_up", "possibly_responded", "unclear"]
    rationale: str = Field(min_length=1, max_length=1500)
    uncertainty: list[str] = Field(max_length=10)
    github: GitHubState


class Coverage(StrictModel):
    pr_id: str
    status: Literal["analyzed", "failed", "rejected_oversize"]
    comments_total: int = Field(ge=0)
    comments_processed: int = Field(ge=0)
    comments_excluded_bots: int = Field(ge=0)
    reason: str | None = None


class Stats(StrictModel):
    comments_total: int = Field(ge=0)
    comments_processed: int = Field(ge=0)
    comments_excluded_bots: int = Field(ge=0)
    elapsed_seconds: float = Field(ge=0)


class Analysis(StrictModel):
    id: str
    snapshot_id: str
    mode: Literal["model", "baseline"]
    scope: Literal["human_review"] = "human_review"
    model: str | None = None
    prompt_version: str
    created_at: str
    complete: bool
    warnings: list[str]
    cards: list[Card]
    coverage: list[Coverage]
    stats: Stats


class Disposition(StrictModel):
    analysis_id: str
    card_id: str
    state: Literal["open", "reviewed"]
    note: str = Field(default="", max_length=2000)
    updated_at: str


class ImportRequest(StrictModel):
    snapshot: dict


class GitHubRequest(StrictModel):
    urls: list[str] = Field(min_length=1, max_length=MAX_PRS)
    owner: str = Field(min_length=1, max_length=39)

    @field_validator("owner")
    @classmethod
    def login(cls, value: str) -> str:
        if not LOGIN.fullmatch(value):
            raise ValueError("Use a valid GitHub login")
        return value

    @field_validator("urls")
    @classmethod
    def urls_valid(cls, value: list[str]) -> list[str]:
        for url in value:
            parse_pr_url(url)
        return list(dict.fromkeys(value))


class AnalysisRequest(StrictModel):
    snapshot_id: str = Field(pattern=r"^[a-f0-9]{64}$")
    mode: Literal["model", "baseline"]


class DispositionRequest(StrictModel):
    state: Literal["open", "reviewed"]
    note: str = Field(default="", max_length=2000)
