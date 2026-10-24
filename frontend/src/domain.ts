import type {
  Analysis,
  Assessment,
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
export const assessmentLabels: Record<Assessment, string> = {
  unassessed: "No disagreement recorded",
  not_a_request: "Not a request",
  reply_not_relevant: "Reply not relevant",
};
export function assessmentFor(
  value: unknown,
  card: Card,
  mode: Analysis["mode"],
): Assessment {
  if (mode !== "model") return "unassessed";
  if (value === "not_a_request") return value;
  if (value === "reply_not_relevant" && card.response) return value;
  return "unassessed";
}
export function normalizeDispositions(
  values: Disposition[],
  analysis: Analysis,
): Disposition[] {
  return values.flatMap((value) => {
    if (
      !value ||
      typeof value !== "object" ||
      value.analysis_id !== analysis.id ||
      (value.state !== "open" && value.state !== "reviewed") ||
      typeof value.note !== "string" ||
      typeof value.updated_at !== "string"
    )
      return [];
    const card = analysis.cards.find((item) => item.id === value.card_id);
    return card
      ? [{
          ...value,
          assessment: assessmentFor(value.assessment, card, analysis.mode),
        }]
      : [];
  });
}
export function evidenceSummary(card: Card): string {
  return card.response
    ? "A reviewer passage is paired with a later author passage. Compare both in context; their relationship has not been verified."
    : "A reviewer passage is shown without a matched author reply. Read the full conversation before deciding what needs attention.";
}
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
function hasOriginalSourceText(body: string, quote: string): boolean {
  // Check the source line, since a selected sentence can omit its leading >.
  // This guards explicit blockquotes, not every form of quoted Markdown.
  let start = body.indexOf(quote);
  while (start !== -1) {
    const end = start + quote.length;
    let cursor = start;
    let hasText = false;
    let quoted = false;
    while (cursor < end) {
      const lineStart = body.lastIndexOf("\n", cursor - 1) + 1;
      const nextLine = body.indexOf("\n", cursor);
      const lineEnd = nextLine === -1 ? body.length : nextLine;
      if (body.slice(cursor, Math.min(end, lineEnd)).trim()) {
        hasText = true;
        if (body.slice(lineStart, lineEnd).trimStart().startsWith(">"))
          quoted = true;
      }
      cursor = lineEnd + 1;
    }
    if (hasText && !quoted) return true;
    start = body.indexOf(quote, start + 1);
  }
  return false;
}
export function verifiedCard(
  snapshot: Snapshot,
  card: Card,
  mode: Analysis["mode"] = "model",
): boolean {
  const { pr, request, response } = sourceFor(snapshot, card);
  if (
    !pr ||
    !request ||
    request.is_bot ||
    request.author.toLowerCase() === pr.author.toLowerCase() ||
    !card.request.quote.trim() ||
    !Number.isFinite(Date.parse(request.created_at)) ||
    !(mode === "baseline"
      ? request.body.includes(card.request.quote)
      : hasOriginalSourceText(request.body, card.request.quote)) ||
    !validSourceUrl(request.url, pr)
  )
    return false;
  if (
    card.response &&
    (!response ||
      !card.response.quote ||
      !hasOriginalSourceText(response.body, card.response.quote) ||
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
  const rejectedCount = analysis.cards.filter(
    (card) => !verifiedCard(snapshot, card, analysis.mode),
  ).length;
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
    ...(rejectedCount
      ? [
          `WARNING: ${rejectedCount} card${rejectedCount === 1 ? " was" : "s were"} rejected because source evidence could not be verified. Inspect Sources; this view is incomplete.`,
        ]
      : []),
    "",
  ];
  for (const card of analysis.cards) {
    const { pr, request, response } = sourceFor(snapshot, card);
    if (!pr || !request || !verifiedCard(snapshot, card, analysis.mode))
      continue;
    lines.push(
      `## ${plainMarkdown(pr.id)} — ${analysis.mode === "baseline" ? "Comment to inspect" : labels[card.interpretation]}`,
      `Request: ${plainMarkdown(card.request.quote)}`,
      `Source: ${request.url}`,
      `Request created: ${plainMarkdown(request.created_at)}`,
      `Request last updated: ${plainMarkdown(request.updated_at)}`,
    );
    if (card.response && response) {
      if (Date.parse(request.updated_at) > Date.parse(response.created_at))
        lines.push(
          "Source caution: request edited after the possible response; original wording at reply time is unknown.",
        );
      lines.push(
        `Possible response: ${plainMarkdown(card.response.quote)}`,
        `Response source: ${response.url}`,
        `Response created: ${plainMarkdown(response.created_at)}`,
        `Response last updated: ${plainMarkdown(response.updated_at)}`,
      );
    }
    lines.push(
      `${analysis.mode === "model" ? "Unverified model explanation" : "Baseline reading note"}: ${plainMarkdown(card.rationale)}`,
      `Uncertainty: ${plainMarkdown(card.uncertainty.join("; ") || "Inspect source context.")}`,
      `Local decision: ${dispositions[card.id]?.state ?? "open"}`,
      ...(analysis.mode === "model" ? [`Local assessment: ${assessmentLabels[assessmentFor(dispositions[card.id]?.assessment, card, analysis.mode)]}. This is your judgment, not a change to model output or GitHub.`] : []),
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
