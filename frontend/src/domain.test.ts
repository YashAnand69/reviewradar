import { describe, expect, it } from "vitest";
import {
  analysisWarnings,
  assessmentFor,
  exportReview,
  normalizeDispositions,
  parseUrls,
  validSourceUrl,
  verifiedCard,
  visibleCards,
} from "./domain";
import type { Analysis, Card, Disposition, Snapshot } from "./types";

// Deliberately synthetic discussion; not product evidence or an accuracy result.
const snapshot: Snapshot = {
  schema_version: 1,
  id: "synthetic-test",
  fetched_at: "2026-10-23T10:00:00Z",
  source: "synthetic",
  owner: "contributor",
  complete: true,
  warnings: [],
  prs: [
    {
      id: "org/repo#1",
      url: "https://github.com/org/repo/pull/1",
      title: "Synthetic test",
      author: "contributor",
      state: "OPEN",
      head_sha: null,
      fetched_at: "2026-10-23T10:00:00Z",
      complete: true,
      warnings: [],
      comments: [
        {
          id: "r1",
          url: "https://github.com/org/repo/pull/1#issuecomment-1",
          author: "reviewer",
          is_bot: false,
          kind: "comment",
          body: "Please add an empty-input test. Also clarify the limit.",
          created_at: "2026-10-21T10:00:00Z",
          updated_at: "2026-10-21T10:00:00Z",
          review_state: null,
          thread_id: null,
          thread_resolved: null,
          thread_outdated: null,
        },
        {
          id: "a1",
          url: "https://github.com/org/repo/pull/1#issuecomment-2",
          author: "contributor",
          is_bot: false,
          kind: "comment",
          body: "Added the empty-input regression test.",
          created_at: "2026-10-22T10:00:00Z",
          updated_at: "2026-10-22T10:00:00Z",
          review_state: null,
          thread_id: null,
          thread_resolved: null,
          thread_outdated: null,
        },
      ],
    },
  ],
};
const card: Card = {
  id: "card-1",
  pr_id: "org/repo#1",
  request: { comment_id: "r1", quote: "Please add an empty-input test." },
  response: {
    comment_id: "a1",
    quote: "Added the empty-input regression test.",
  },
  category: "change",
  interpretation: "possibly_responded",
  rationale: "A later author comment mentions the requested test.",
  uncertainty: ["This does not verify the implementation."],
  github: {
    review_state: null,
    thread_resolved: false,
    thread_outdated: false,
  },
};
const analysis: Analysis = {
  id: "analysis-1",
  snapshot_id: snapshot.id,
  mode: "model",
  scope: "human_review",
  model: "synthetic-test-model",
  prompt_version: "test",
  created_at: "2026-10-23T10:00:00Z",
  complete: true,
  warnings: [],
  cards: [card],
  coverage: [
    {
      pr_id: card.pr_id,
      status: "analyzed",
      comments_total: 2,
      comments_processed: 2,
      comments_excluded_bots: 0,
      reason: null,
    },
  ],
  stats: {
    comments_total: 2,
    comments_processed: 2,
    comments_excluded_bots: 0,
    elapsed_seconds: 1,
  },
};
describe("bound evidence rendering", () => {
  it("accepts exact same-PR later author evidence without declaring a fix", () => {
    expect(verifiedCard(snapshot, card)).toBe(true);
    expect(exportReview(snapshot, analysis, {})).toContain(
      "not a verified code fix",
    );
  });
  it.each([
    "javascript:alert(1)",
    "https://evil.example/org/repo/pull/1#issuecomment-1",
    "https://github.com/org/other/pull/1#issuecomment-1",
    "https://github.com/org/repo/pull/1?redirect=evil#issuecomment-1",
    "https://user@github.com/org/repo/pull/1#issuecomment-1",
  ])("rejects unsafe source %s", (url) =>
    expect(validSourceUrl(url, snapshot.prs[0])).toBe(false),
  );
  it("rejects a paraphrase, wrong source and response from another PR", () => {
    expect(
      verifiedCard(snapshot, {
        ...card,
        request: { ...card.request, quote: "Please add tests." },
      }),
    ).toBe(false);
    expect(verifiedCard(snapshot, { ...card, pr_id: "org/other#1" })).toBe(
      false,
    );
    expect(
      verifiedCard(snapshot, {
        ...card,
        response: { comment_id: "missing", quote: "done" },
      }),
    ).toBe(false);
  });
  it("rejects earlier, same-time, non-author and malformed-date responses", () => {
    for (const mutation of [
      { created_at: "2026-10-20T10:00:00Z" },
      { created_at: snapshot.prs[0].comments[0].created_at },
      { author: "someone-else" },
      { created_at: "not-a-date" },
    ]) {
      const changed = structuredClone(snapshot);
      Object.assign(changed.prs[0].comments[1], mutation);
      expect(verifiedCard(changed, card)).toBe(false);
    }
  });
  it("rejects author updates and bot comments as human reviewer requests", () => {
    for (const mutation of [{ is_bot: true }, { author: "contributor" }]) {
      const changed = structuredClone(snapshot);
      Object.assign(changed.prs[0].comments[0], mutation);
      expect(verifiedCard(changed, card)).toBe(false);
    }
  });
  it("does not label a response without evidence as possibly responded", () =>
    expect(verifiedCard(snapshot, { ...card, response: null })).toBe(false));
  it("rejects requests and replies selected only from explicit blockquote source lines", () => {
    for (const index of [0, 1]) {
      const changed = structuredClone(snapshot);
      changed.prs[0].comments[index].body =
        `> Earlier context. ${changed.prs[0].comments[index].body}`;
      expect(verifiedCard(changed, card)).toBe(false);
    }
  });
  it("retains original prose after quoted context, including repeated words", () => {
    const changed = structuredClone(snapshot);
    for (const comment of changed.prs[0].comments)
      comment.body = `> ${comment.body}\n\n${comment.body}`;
    expect(verifiedCard(changed, card)).toBe(true);
  });
  it("rejects an evidence span that mixes quoted and original source lines", () => {
    const changed = structuredClone(snapshot);
    const quote = "> Previous request.\nPlease add an empty-input test.";
    changed.prs[0].comments[0].body = quote;
    expect(
      verifiedCard(changed, {
        ...card,
        request: { ...card.request, quote },
      }),
    ).toBe(false);
  });
  it("retains quoted context in the explicitly non-semantic baseline reading list", () => {
    const changed = structuredClone(snapshot);
    const quote = "> Previous request.\nPlease add an empty-input test.";
    changed.prs[0].comments[0].body = quote;
    const baselineCard: Card = {
      ...card,
      request: { ...card.request, quote },
      response: null,
      interpretation: "unclear",
    };
    expect(verifiedCard(changed, baselineCard, "baseline")).toBe(true);
    expect(
      exportReview(
        changed,
        {
          ...analysis,
          mode: "baseline",
          model: null,
          cards: [baselineCard],
        },
        {},
      ),
    ).toContain("Comment to inspect");
  });
});
describe("attention filters and coverage", () => {
  it("keeps possible responses and reviewed cards visible by default", () => {
    const dispositions: Record<string, Disposition> = {
      [card.id]: {
        analysis_id: analysis.id,
        card_id: card.id,
        state: "reviewed",
        note: "Read original",
        updated_at: analysis.created_at,
      },
    };
    expect(
      visibleCards([card], dispositions, {
        interpretation: "all",
        pr: "all",
        includeReviewed: true,
        search: "",
      }),
    ).toHaveLength(1);
    expect(
      visibleCards([card], dispositions, {
        interpretation: "all",
        pr: "all",
        includeReviewed: false,
        search: "",
      }),
    ).toHaveLength(0);
  });
  it("preserves partial-PR warnings even with zero cards", () => {
    const failed = {
      ...analysis,
      complete: false,
      cards: [],
      coverage: [
        {
          ...analysis.coverage[0],
          status: "rejected_oversize" as const,
          reason: "Conversation exceeds context budget.",
        },
      ],
    };
    expect(analysisWarnings(snapshot, failed).join(" ")).toContain(
      "zero-card result does not clear",
    );
    expect(analysisWarnings(snapshot, failed).join(" ")).toContain(
      "exceeds context budget",
    );
  });
  it("does not lose source incompleteness after successful model output", () =>
    expect(
      analysisWarnings({ ...snapshot, complete: false }, analysis).join(" "),
    ).toContain("Source coverage is incomplete"));
});
describe("safe import and export", () => {
  it("exports human disagreement independently from the original model interpretation and reviewed status", () => {
    const output = exportReview(snapshot, analysis, {
      [card.id]: { analysis_id: analysis.id, card_id: card.id, state: "open", note: "Inspect manually", assessment: "reply_not_relevant", updated_at: analysis.created_at },
    });
    expect(output).toContain("Possible response found");
    expect(output).toContain("Local decision: open");
    expect(output).toContain("Local assessment: Reply not relevant. This is your judgment");
    expect(output).toContain("Inspect manually");
  });
  it("labels original model rationale as unverified without mutating saved analysis", () => {
    const before = structuredClone(analysis);
    const output = exportReview(snapshot, analysis, {});
    expect(output).toContain("Unverified model explanation: A later author comment mentions the requested test\\.");
    expect(analysis).toEqual(before);
    const baselineOutput = exportReview(snapshot, { ...analysis, mode: "baseline", model: null }, {});
    expect(baselineOutput).toContain("Baseline reading note: A later author comment mentions the requested test\\.");
    expect(baselineOutput).not.toContain("Unverified model explanation:");
  });
  it("normalizes legacy replay decisions and rejects cross-analysis or malformed browser records", () => {
    const legacy: Disposition = { analysis_id: analysis.id, card_id: card.id, state: "reviewed", note: "Kept", updated_at: analysis.created_at };
    expect(normalizeDispositions([legacy], analysis)).toEqual([{ ...legacy, assessment: "unassessed" }]);
    expect(normalizeDispositions([null, { ...legacy, analysis_id: "other" }, { ...legacy, note: {} }] as never, analysis)).toEqual([]);
    expect(assessmentFor("reply_not_relevant", { ...card, response: null }, "model")).toBe("unassessed");
    expect(assessmentFor("not_a_request", card, "baseline")).toBe("unassessed");
    expect(assessmentFor("invented", card, "model")).toBe("unassessed");
  });
  it("accepts and deduplicates canonical PR URLs", () =>
    expect(
      parseUrls(
        "https://github.com/org/repo/pull/1\nhttps://github.com/org/repo/pull/1",
      ),
    ).toHaveLength(1));
  it("rejects query strings, shell-like text and more than five PRs", () => {
    for (const input of [
      "https://github.com/org/repo/pull/1?x=1",
      "$(echo unsafe)",
      Array.from(
        { length: 6 },
        (_, index) => `https://github.com/org/repo/pull/${index + 1}`,
      ).join("\n"),
    ])
      expect(() => parseUrls(input)).toThrow();
  });
  it("exports baseline mode without semantic interpretation claims", () => {
    const output = exportReview(
      snapshot,
      { ...analysis, mode: "baseline", model: null },
      {},
    );
    expect(output).toContain("Comment to inspect");
    expect(output).not.toContain("— Possible response found");
  });
  it("preserves source timestamps and cautions when a request changed after its reply", () => {
    const changed = structuredClone(snapshot);
    changed.prs[0].comments[0].updated_at = "2026-10-22T10:01:00Z";
    const output = exportReview(changed, analysis, {}).replaceAll("\\-", "-");
    expect(output).toContain("Request created: 2026-10-21T10:00:00Z");
    expect(output).toContain("Request last updated: 2026-10-22T10:01:00Z");
    expect(output).toContain("Response created: 2026-10-22T10:00:00Z");
    expect(output).toContain("Response last updated: 2026-10-22T10:00:00Z");
    expect(output).toContain(
      "Source caution: request edited after the possible response; original wording at reply time is unknown.",
    );
    expect(exportReview(snapshot, analysis, {})).not.toContain(
      "Source caution:",
    );
  });
  it("warns when an unbound replay card is rejected rather than silently exporting an empty view", () => {
    const output = exportReview(
      snapshot,
      {
        ...analysis,
        cards: [
          { ...card, request: { ...card.request, quote: "Invented ask" } },
        ],
      },
      {},
    );
    expect(output).toContain(
      "WARNING: 1 card was rejected because source evidence could not be verified. Inspect Sources; this view is incomplete.",
    );
    expect(output).not.toContain("Invented ask");
    expect(output).not.toContain("## org/repo");
  });
  it("escapes note markup and retains source/completeness metadata", () => {
    const note = "## Forged section\n[click](javascript:alert(1)) <script>";
    const output = exportReview(
      snapshot,
      { ...analysis, complete: false },
      {
        [card.id]: {
          analysis_id: analysis.id,
          card_id: card.id,
          state: "reviewed",
          note,
          updated_at: analysis.created_at,
        },
      },
    );
    expect(output).toContain("Captured: 2026-10-23");
    expect(output).toContain("WARNING:");
    expect(output).not.toContain("## Forged section");
    expect(output).not.toContain("[click]");
    expect(output).not.toContain("<script>");
    expect(output).toContain(snapshot.prs[0].comments[0].url);
  });
});
