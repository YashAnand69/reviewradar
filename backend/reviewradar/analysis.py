"""Human-review analysis, evidence validation and honest coverage accounting."""

import hashlib
import re
import time
import uuid

from .config import Settings
from .model import (
    Candidate,
    LocalModel,
    ModelFailure,
    Oversize,
    PROMPT_VERSION,
    eligible_source_quote,
)
from .schemas import (
    Analysis,
    Card,
    Coverage,
    Evidence,
    GitHubState,
    PR,
    Snapshot,
    Stats,
    timestamp,
    utc_now,
)


def card_id(pr_id: str, source_id: str, quote: str) -> str:
    return hashlib.sha256(f"{pr_id}\0{source_id}\0{quote}".encode()).hexdigest()[:24]


def validate_candidates(candidates: list[Candidate], pr: PR) -> list[Card]:
    comments = {comment.id: comment for comment in pr.comments}
    cards: list[Card] = []
    seen: set[tuple[str, str]] = set()
    for candidate in candidates:
        request = comments.get(candidate.request_id)
        if (
            request is None
            or request.is_bot
            or request.author.casefold() == pr.author.casefold()
        ):
            raise ModelFailure(
                "Model evidence included an ineligible request source. This PR remains incomplete."
            )
        if not eligible_source_quote(request.body, candidate.request_quote):
            raise ModelFailure(
                "Model request quote did not match its original source. This PR remains incomplete."
            )
        response_evidence = None
        if (candidate.response_id is None) != (candidate.response_quote is None):
            raise ModelFailure(
                "Model response needs both a valid ID and an exact quote. This PR remains incomplete."
            )
        if candidate.response_id is not None:
            response = comments.get(candidate.response_id)
            if (
                response is None
                or response.is_bot
                or response.author.casefold() != pr.author.casefold()
                or timestamp(response.created_at) <= timestamp(request.created_at)
            ):
                raise ModelFailure(
                    "Model response was not a strictly later author comment in this PR. This PR remains incomplete."
                )
            if not candidate.response_quote or not eligible_source_quote(
                response.body, candidate.response_quote
            ):
                raise ModelFailure(
                    "Model response quote did not match eligible original author evidence. This PR remains incomplete."
                )
            if candidate.interpretation == "follow_up":
                raise ModelFailure(
                    "Model response and interpretation contradicted one another. This PR remains incomplete."
                )
            response_evidence = Evidence(
                comment_id=response.id, quote=candidate.response_quote
            )
        elif candidate.interpretation == "possibly_responded":
            raise ModelFailure(
                "Model claimed a possible response without evidence. This PR remains incomplete."
            )
        duplicate_key = (request.id, candidate.request_quote)
        if duplicate_key in seen:
            continue  # Exact repeated spans have one deterministic card; different asks remain separate.
        seen.add(duplicate_key)
        cards.append(
            Card(
                id=card_id(pr.id, request.id, candidate.request_quote),
                pr_id=pr.id,
                request=Evidence(comment_id=request.id, quote=candidate.request_quote),
                response=response_evidence,
                category=candidate.category,
                interpretation=candidate.interpretation,
                rationale=candidate.rationale,
                uncertainty=candidate.uncertainty,
                github=GitHubState(
                    review_state=request.review_state,
                    thread_resolved=request.thread_resolved,
                    thread_outdated=request.thread_outdated,
                ),
            )
        )
    return cards


def baseline(pr: PR) -> list[Card]:
    cards = []
    for comment in pr.comments:
        if (
            comment.is_bot
            or comment.author.casefold() == pr.author.casefold()
            or not comment.body.strip()
        ):
            continue
        quote = comment.body[:600]
        cards.append(
            Card(
                id=card_id(pr.id, comment.id, quote),
                pr_id=pr.id,
                request=Evidence(comment_id=comment.id, quote=quote),
                response=None,
                category="unclear",
                interpretation="unclear",
                rationale="Chronology baseline: a human reviewer comment to inspect. No request extraction or response matching was performed.",
                uncertainty=[
                    "This may not contain a request.",
                    "Inspect the original discussion before deciding what needs attention.",
                ],
                github=GitHubState(
                    review_state=comment.review_state,
                    thread_resolved=comment.thread_resolved,
                    thread_outdated=comment.thread_outdated,
                ),
            )
        )
    return cards


def run_analysis(
    snapshot: Snapshot,
    mode: str,
    settings: Settings,
    *,
    model: LocalModel | None = None,
) -> Analysis:
    started = time.monotonic()
    cards: list[Card] = []
    coverage: list[Coverage] = []
    warnings = list(snapshot.warnings)
    model = model or LocalModel(settings)
    for pr in snapshot.prs:
        bots = sum(comment.is_bot for comment in pr.comments)
        item = Coverage(
            pr_id=pr.id,
            status="analyzed",
            comments_total=len(pr.comments),
            comments_processed=0,
            comments_excluded_bots=bots,
        )
        try:
            if not pr.complete and not pr.comments:
                raise ModelFailure(
                    "No comments were available from an incomplete source. Inspect the original PR."
                )
            if mode == "baseline":
                result = baseline(pr)
            elif mode == "model":
                eligible_reviewers = [
                    c
                    for c in pr.comments
                    if not c.is_bot
                    and c.author.casefold() != pr.author.casefold()
                    and c.body.strip()
                ]
                result = (
                    validate_candidates(model.analyze(pr), pr)
                    if eligible_reviewers
                    else []
                )
            else:
                raise ValueError("Unsupported analysis mode")
            cards.extend(result)
            item.comments_processed = len(pr.comments) - bots
            if not pr.complete:
                item.reason = "Available comments analyzed; source incomplete. Omitted discussion may change the interpretation."
                warnings.append(f"{pr.id}: {item.reason}")
        except Oversize as exc:
            item.status = "rejected_oversize"
            item.reason = str(exc)
            warnings.append(f"{pr.id}: {exc}")
        except ModelFailure as exc:
            item.status = "failed"
            item.reason = str(exc)
            warnings.append(f"{pr.id}: {exc}")
        coverage.append(item)
    return Analysis(
        id=uuid.uuid4().hex,
        snapshot_id=snapshot.id,
        mode=mode,
        scope="human_review",
        model=settings.model_name if mode == "model" else None,
        prompt_version=PROMPT_VERSION if mode == "model" else "chronology-v1",
        created_at=utc_now(),
        complete=snapshot.complete
        and all(item.status == "analyzed" for item in coverage),
        warnings=list(dict.fromkeys(warnings)),
        cards=cards,
        coverage=coverage,
        stats=Stats(
            comments_total=sum(c.comments_total for c in coverage),
            comments_processed=sum(c.comments_processed for c in coverage),
            comments_excluded_bots=sum(c.comments_excluded_bots for c in coverage),
            elapsed_seconds=round(time.monotonic() - started, 3),
        ),
    )


def validate_bound_analysis(analysis: Analysis, snapshot: Snapshot) -> None:
    """Reject a bundled saved run that does not correspond to its accompanying evidence."""
    if analysis.snapshot_id != snapshot.id:
        raise ValueError("Saved analysis does not match the snapshot identity")
    prs = {pr.id: pr for pr in snapshot.prs}
    if len(analysis.coverage) != len(prs) or {
        item.pr_id for item in analysis.coverage
    } != set(prs):
        raise ValueError(
            "Saved analysis coverage does not identify every PR exactly once"
        )
    if len({card.id for card in analysis.cards}) != len(analysis.cards):
        raise ValueError("Saved analysis contains duplicate card IDs")
    coverage = {item.pr_id: item for item in analysis.coverage}
    for item in analysis.coverage:
        pr = prs[item.pr_id]
        bots = sum(comment.is_bot for comment in pr.comments)
        if (
            item.comments_total != len(pr.comments)
            or item.comments_excluded_bots != bots
            or item.comments_processed > len(pr.comments) - bots
        ):
            raise ValueError("Saved analysis source counts are inconsistent")
        if (
            item.status == "analyzed"
            and item.comments_processed != len(pr.comments) - bots
        ):
            raise ValueError("Saved analysis did not account for all human inputs")
    if analysis.complete and (
        not snapshot.complete
        or any(item.status != "analyzed" for item in analysis.coverage)
    ):
        raise ValueError("Saved analysis falsely claims completeness")
    if (
        analysis.stats.comments_total
        != sum(item.comments_total for item in analysis.coverage)
        or analysis.stats.comments_processed
        != sum(item.comments_processed for item in analysis.coverage)
        or analysis.stats.comments_excluded_bots
        != sum(item.comments_excluded_bots for item in analysis.coverage)
    ):
        raise ValueError("Saved analysis aggregate counts are inconsistent")
    for card in analysis.cards:
        pr = prs.get(card.pr_id)
        if pr is None or coverage[card.pr_id].status != "analyzed":
            raise ValueError("Saved card belongs to an unanalyzed or unknown PR")
        if analysis.mode == "baseline":
            originals = {candidate.id: candidate for candidate in baseline(pr)}
            if (
                card.id not in originals
                or card.model_dump() != originals[card.id].model_dump()
            ):
                raise ValueError(
                    "Saved baseline card is not a deterministic comment view"
                )
        else:
            candidate = Candidate(
                request_id=card.request.comment_id,
                request_quote=card.request.quote,
                response_id=card.response.comment_id if card.response else None,
                response_quote=card.response.quote if card.response else None,
                category=card.category,
                interpretation=card.interpretation,
                rationale=card.rationale,
                uncertainty=card.uncertainty,
            )
            validated = validate_candidates([candidate], pr)[0]
            if validated.github != card.github:
                raise ValueError("Saved card GitHub metadata differs from its source")


def markdown_text(text: str) -> str:
    return re.sub(r"([\\`*_{}\[\]()#+.!<>|~\-])", r"\\\1", text)


def export_markdown(analysis: Analysis, snapshot: Snapshot, dispositions: list) -> str:
    decisions = {decision.card_id: decision for decision in dispositions}
    lines = [
        "# ReviewRadar inspection sheet",
        "",
        f"Snapshot: {snapshot.fetched_at}",
        f"Analysis: {analysis.created_at}",
        f"Mode: {analysis.mode}; model: {markdown_text(analysis.model or 'none')}",
        "Scope: human review. Bot comments remain in Sources and are excluded from this queue.",
        f"Complete within declared scope: {'yes' if analysis.complete else 'NO — inspect incomplete sources'}",
        "",
        "A possible response is conversational evidence, not verification of a code fix. Local decisions do not change GitHub.",
        "",
    ]
    for warning in analysis.warnings:
        lines.append(f"Warning: {markdown_text(warning)}")
    for item in analysis.coverage:
        lines.append(
            f"Coverage: {markdown_text(item.pr_id)} — {item.status}; {item.comments_processed}/{item.comments_total - item.comments_excluded_bots} human inputs processed ({item.comments_total} total sources); {item.comments_excluded_bots} bots excluded."
        )
        if item.reason:
            lines.append(markdown_text(item.reason))
    prs = {pr.id: pr for pr in snapshot.prs}
    for index, card in enumerate(analysis.cards, 1):
        pr = prs[card.pr_id]
        comments = {comment.id: comment for comment in pr.comments}
        request = comments[card.request.comment_id]
        decision = decisions.get(card.id)
        lines.extend(
            [
                "",
                f"## {index}. {markdown_text(card.pr_id)}",
                f"Interpretation: {card.interpretation}",
                f"[Original request]({request.url})",
                "",
                "> " + markdown_text(card.request.quote).replace("\n", "\n> "),
                "",
            ]
        )
        if card.response:
            response = comments[card.response.comment_id]
            if timestamp(request.updated_at) > timestamp(response.created_at):
                lines.append(
                    "Source caution: request edited after the possible response; original wording at reply time is unknown."
                )
            lines.extend(
                [
                    f"[Possible later response]({response.url})",
                    "",
                    "> " + markdown_text(card.response.quote).replace("\n", "\n> "),
                    "",
                ]
            )
        lines.append(markdown_text(card.rationale))
        for uncertainty in card.uncertainty:
            lines.append(f"Uncertainty: {markdown_text(uncertainty)}")
        lines.append(f"Local decision: {decision.state if decision else 'open'}")
        if decision and decision.note:
            lines.append(f"Local note: {markdown_text(decision.note)}")
    if not analysis.cards:
        lines.extend(
            [
                "",
                "No cards were identified in the available inputs. This does not certify that no review work remains.",
            ]
        )
    return "\n".join(lines) + "\n"
