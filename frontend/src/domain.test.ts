import { describe, expect, it } from "vitest";
import {
  analysisWarnings,
  exportReview,
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
