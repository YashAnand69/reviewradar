import type {
  Analysis,
  Card,
  Disposition,
  PullRequest,
  Snapshot,
  SourceComment,
} from "./types";

export const labels = {
  follow_up: "Follow-up to inspect",
  possibly_responded: "Possible response found",
  unclear: "Needs interpretation",
};
export function displayDate(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? "Date unavailable"
    : date.toLocaleString(undefined, {
        dateStyle: "medium",
        timeStyle: "short",
      });
}
export function sourceFor(
  snapshot: Snapshot,
  card: Card,
): {
  pr: PullRequest | undefined;
  request: SourceComment | undefined;
  response: SourceComment | undefined;
} {
  const pr = snapshot.prs.find((p) => p.id === card.pr_id);
  return {
    pr,
    request: pr?.comments.find((c) => c.id === card.request.comment_id),
    response: pr?.comments.find((c) => c.id === card.response?.comment_id),
  };
}
export function validSourceUrl(url: string, pr: PullRequest): boolean {
  try {
    const parsed = new URL(url);
    const canonical = new URL(pr.url);
    return (
      parsed.protocol === "https:" &&
      parsed.hostname === "github.com" &&
      !parsed.username &&
      !parsed.password &&
      !parsed.port &&
      parsed.pathname === canonical.pathname &&
      !parsed.search &&
      /^#(?:issuecomment-\d+|pullrequestreview-\d+|discussion_r\d+)$/.test(
        parsed.hash,
      )
    );
  } catch {
    return false;
  }
}
export function verifiedCard(snapshot: Snapshot, card: Card): boolean {
  const { pr, request, response } = sourceFor(snapshot, card);
  if (
    !pr ||
    !request ||
    request.is_bot ||
    request.author.toLowerCase() === pr.author.toLowerCase() ||
    !card.request.quote.trim() ||
    !Number.isFinite(Date.parse(request.created_at)) ||
    !request.body.includes(card.request.quote) ||
    !validSourceUrl(request.url, pr)
  )
    return false;
  if (
    card.response &&
    (!response ||
      !card.response.quote ||
      !response.body.includes(card.response.quote) ||
      !validSourceUrl(response.url, pr) ||
      response.is_bot ||
      response.author.toLowerCase() !== pr.author.toLowerCase() ||
      !Number.isFinite(Date.parse(response.created_at)) ||
      !Number.isFinite(Date.parse(request.created_at)) ||
      Date.parse(response.created_at) <= Date.parse(request.created_at))
  )
    return false;
  return !(card.interpretation === "possibly_responded" && !card.response);
}
export function visibleCards(
  cards: Card[],
  dispositions: Record<string, Disposition>,
  options: {
    interpretation: string;
    pr: string;
    includeReviewed: boolean;
    search: string;
  },
): Card[] {
  return cards
    .filter(
      (c) =>
        (options.interpretation === "all" ||
          c.interpretation === options.interpretation) &&
        (options.pr === "all" || c.pr_id === options.pr) &&
        (options.includeReviewed || dispositions[c.id]?.state !== "reviewed") &&
        `${c.request.quote} ${c.pr_id} ${c.rationale}`
          .toLowerCase()
          .includes(options.search.trim().toLowerCase()),
    )
    .sort(
      (a, b) =>
        ({ follow_up: 0, unclear: 1, possibly_responded: 2 })[
          a.interpretation
        ] -
        { follow_up: 0, unclear: 1, possibly_responded: 2 }[b.interpretation],
    );
}
export function analysisWarnings(
  snapshot: Snapshot,
  analysis: Analysis | null,
): string[] {
  return [
    ...new Set([
      ...(!snapshot.complete
        ? ["Source coverage is incomplete. Inspect the original conversations."]
        : []),
      ...snapshot.warnings,
      ...snapshot.prs.flatMap((p) =>
        p.complete
          ? p.warnings
          : [`${p.id}: source coverage is incomplete.`, ...p.warnings],
      ),
      ...(analysis && !analysis.complete
        ? [
            "Analysis is incomplete. A zero-card result does not clear the selected PRs.",
          ]
        : []),
      ...(analysis?.warnings ?? []),
      ...(analysis?.coverage
        .filter((c) => c.status !== "analyzed")
        .map((c) => `${c.pr_id}: ${c.reason ?? c.status}`) ?? []),
    ]),
  ];
}
export function plainMarkdown(text: string): string {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replace(/[\\`*_{}\[\]()#+.!|~-]/g, "\\$&");
}
export function exportReview(
  snapshot: Snapshot,
  analysis: Analysis,
  dispositions: Record<string, Disposition>,
): string {
  const lines = [
    "# ReviewRadar — local review sheet",
    "",
    `Snapshot: ${snapshot.id}`,
    `Captured: ${snapshot.fetched_at}`,
    `Analysis: ${analysis.id}`,
    `Mode: ${analysis.mode} · ${analysis.model ?? "no model"}`,
    "Scope: human review. Automated comments remain in Sources.",
    "A possible response is not a verified code fix. Local decisions do not change GitHub.",
    "",
    ...analysisWarnings(snapshot, analysis).map(
      (w) => `WARNING: ${plainMarkdown(w)}`,
    ),
    "",
  ];
  for (const card of analysis.cards) {
    const { pr, request, response } = sourceFor(snapshot, card);
    if (!pr || !request || !verifiedCard(snapshot, card)) continue;
    lines.push(
      `## ${plainMarkdown(pr.id)} — ${analysis.mode === "baseline" ? "Comment to inspect" : labels[card.interpretation]}`,
      `Request: ${plainMarkdown(card.request.quote)}`,
      `Source: ${request.url}`,
    );
    if (card.response && response)
      lines.push(
        `Possible response: ${plainMarkdown(card.response.quote)}`,
        `Response source: ${response.url}`,
      );
    lines.push(
      `Uncertainty: ${plainMarkdown(card.uncertainty.join("; ") || "Inspect source context.")}`,
      `Local decision: ${dispositions[card.id]?.state ?? "open"}`,
      `Note: ${plainMarkdown(dispositions[card.id]?.note ?? "")}`,
      "",
    );
  }
  return lines.join("\n");
}
export function parseUrls(value: string): string[] {
  const urls = [
    ...new Set(
      value
        .split(/\s+/)
        .map((x) => x.trim().replace(/\/$/, ""))
        .filter(Boolean),
    ),
  ];
  if (!urls.length || urls.length > 5)
    throw new Error("Enter between one and five public pull-request URLs.");
  for (const url of urls)
    if (
      !/^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+\/pull\/[1-9][0-9]*\/?$/.test(
        url,
      )
    )
      throw new Error(
        "Use canonical https://github.com/owner/repo/pull/123 URLs, without queries or fragments.",
      );
  return urls;
}
