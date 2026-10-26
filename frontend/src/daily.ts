import { parseUrls } from "./domain";
import type { PullRequest, Snapshot, SourceComment } from "./types";

export const WATCHLIST_KEY = "reviewradar:selections:v1";
export interface SavedSelection {
  owner: string;
  urls: string[];
  snapshotId: string;
  capturedAt: string;
}
export function selectionKey(owner: string, urls: string[]): string {
  return JSON.stringify([owner.toLowerCase(), urls.map((url) => url.toLowerCase()).sort()]);
}
export function parseSelections(value: string | null): SavedSelection[] {
  if (!value) return [];
  if (value.length > 16000) throw new Error("Saved selections are too large.");
  const data: unknown = JSON.parse(value);
  if (!data || typeof data !== "object" || !("version" in data) || data.version !== 1 ||
      !("selections" in data) || !Array.isArray(data.selections) || data.selections.length > 5)
    throw new Error("Saved selections have an unsupported format.");
  const seen = new Set<string>();
  return data.selections.map((entry: unknown) => {
    if (!entry || typeof entry !== "object" || !("owner" in entry) || typeof entry.owner !== "string" ||
        !/^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$/.test(entry.owner) ||
        !("urls" in entry) || !Array.isArray(entry.urls) || !entry.urls.every((url) => typeof url === "string") ||
        !("snapshotId" in entry) || typeof entry.snapshotId !== "string" || !/^[a-f0-9]{64}$/.test(entry.snapshotId) ||
        !("capturedAt" in entry) || typeof entry.capturedAt !== "string" || !Number.isFinite(Date.parse(entry.capturedAt)))
      throw new Error("A saved selection is invalid.");
    const urls = parseUrls(entry.urls.join("\n"));
    if (urls.length !== entry.urls.length || urls.some((url) => new URL(url).href !== url))
      throw new Error("A saved selection contains invalid PR URLs.");
    const key = selectionKey(entry.owner, urls);
    if (seen.has(key)) throw new Error("A saved selection is repeated.");
    seen.add(key);
    return { owner: entry.owner, urls, snapshotId: entry.snapshotId, capturedAt: entry.capturedAt };
  });
}
export function selectionFrom(snapshot: Snapshot): SavedSelection {
  if (snapshot.source !== "github") throw new Error("Save selections from a public GitHub import.");
  const selection = { owner: snapshot.owner, urls: snapshot.prs.map((pr) => pr.url), snapshotId: snapshot.id, capturedAt: snapshot.fetched_at };
  return parseSelections(JSON.stringify({ version: 1, selections: [selection] }))[0];
}

export interface SourceChange {
  kind: "new" | "edited" | "missing";
  role: "reviewer" | "author" | "automated";
  pr: PullRequest;
  comment: SourceComment;
  previous?: SourceComment;
}
export interface CaptureChanges {
  previousAt: string;
  currentAt: string;
  complete: boolean;
  sources: SourceChange[];
  states: { prId: string; description: string }[];
}
export function compareCaptures(previous: Snapshot, current: Snapshot): CaptureChanges | null {
  if (previous.owner.toLowerCase() !== current.owner.toLowerCase() ||
      selectionKey(previous.owner, previous.prs.map((pr) => pr.url)) !== selectionKey(current.owner, current.prs.map((pr) => pr.url)) ||
      !Number.isFinite(Date.parse(previous.fetched_at)) || !Number.isFinite(Date.parse(current.fetched_at)) ||
      Date.parse(current.fetched_at) < Date.parse(previous.fetched_at)) return null;
  const result: CaptureChanges = {
    previousAt: previous.fetched_at, currentAt: current.fetched_at,
    complete: previous.complete && current.complete && previous.prs.every((pr) => pr.complete) && current.prs.every((pr) => pr.complete),
    sources: [], states: [],
  };
  for (const pr of current.prs) {
    const before = previous.prs.find((old) => old.url.toLowerCase() === pr.url.toLowerCase());
    if (!before) return null;
    if (before.state !== pr.state) result.states.push({ prId: pr.id, description: `PR state: ${before.state.toLowerCase()} → ${pr.state.toLowerCase()}` });
    if (before.head_sha !== pr.head_sha) result.states.push({ prId: pr.id, description: "Head revision changed. This does not verify a fix." });
    if (before.title !== pr.title) result.states.push({ prId: pr.id, description: `Title changed: ${before.title} → ${pr.title}` });
    const oldComments = new Map(before.comments.map((comment) => [comment.id, comment]));
    const role = (comment: SourceComment) => comment.is_bot ? "automated" as const : comment.author.toLowerCase() === pr.author.toLowerCase() ? "author" as const : "reviewer" as const;
    for (const comment of pr.comments) {
      const old = oldComments.get(comment.id);
      if (!old) result.sources.push({ kind: "new", role: role(comment), pr, comment });
      else if (old.body !== comment.body || old.review_state !== comment.review_state ||
          old.thread_resolved !== comment.thread_resolved || old.thread_outdated !== comment.thread_outdated ||
          old.author !== comment.author || old.is_bot !== comment.is_bot || old.kind !== comment.kind || old.url !== comment.url) {
        result.sources.push({ kind: "edited", role: role(comment), pr, comment, previous: old });
      }
      oldComments.delete(comment.id);
    }
    // Absence from a capture is never proof of deletion, even with complete intake.
    for (const comment of oldComments.values()) result.sources.push({ kind: "missing", role: role(comment), pr: before, comment });
  }
  return result;
}
