import { describe, expect, it } from "vitest";
import packet from "../public/sample.json";
import { compareCaptures, parseSelections, selectionFrom } from "./daily";
import type { Snapshot } from "./types";
const snapshot = () => structuredClone(packet.snapshot) as Snapshot;
describe("daily capture comparisons", () => {
  it("distinguishes new author updates, edited reviewer text and missing evidence without mutating snapshots", () => {
    const old = snapshot(); const next = snapshot();
    next.fetched_at = "2026-10-26T10:00:00Z";
    next.prs[0].comments[0].body += " edited";
    const added = {...next.prs[0].comments[0], id:"comment:999", author:next.prs[0].author};
    next.prs[0].comments.push(added);
    next.prs[1].comments.pop();
    const serialized = JSON.stringify(old);
    const changes = compareCaptures(old,next)!;
    expect(changes.sources.some(item => item.kind === "edited")).toBe(true);
    expect(changes.sources.some(item => item.kind === "new" && item.role === "author")).toBe(true);
    expect(changes.sources.some(item => item.kind === "missing")).toBe(true);
    expect(changes.complete).toBe(false);
    expect(JSON.stringify(old)).toBe(serialized);
  });
  it("refuses unrelated or backwards comparisons", () => {
    const old=snapshot(); const next=snapshot(); next.owner="someone";
    expect(compareCaptures(old,next)).toBeNull();
    next.owner=old.owner; next.fetched_at="2000-01-01T00:00:00Z";
    expect(compareCaptures(old,next)).toBeNull();
  });
  it("treats unchanged captured content as an empty comparison, not a completed task",()=>{
    const old=snapshot();const next=snapshot();next.fetched_at="2026-10-26T10:00:00Z";
    expect(compareCaptures(old,next)?.sources).toEqual([]);
    next.prs[0].state="CLOSED";
    expect(compareCaptures(old,next)?.states).toHaveLength(1);
  });
});
describe("saved public selections",()=>{
  it("round trips only public GitHub selections",()=>{
    const source=snapshot(); source.source="github";
    const selection=selectionFrom(source);
    expect(parseSelections(JSON.stringify({version:1,selections:[selection]}))).toEqual([selection]);
    source.source="import"; expect(()=>selectionFrom(source)).toThrow();
  });
  it("rejects tampered URLs, duplicates, invalid identities and oversized storage",()=>{
    const source=snapshot();source.source="github";const entry=selectionFrom(source);
    for(const item of [{...entry,urls:["https://github.com.evil.test/a/b/pull/1"]},{...entry,snapshotId:"../secret"},{...entry,urls:["https://github.com/a/b/pull/1?token=x"]}])
      expect(()=>parseSelections(JSON.stringify({version:1,selections:[item]}))).toThrow();
    expect(()=>parseSelections(JSON.stringify({version:1,selections:[entry,entry]}))).toThrow();
    expect(()=>parseSelections("x".repeat(16001))).toThrow();
  });
});

it("flags missing sources with incomplete coverage instead of implying deletion", () => {
  const old=snapshot();const next=snapshot();next.fetched_at="2026-10-26T10:00:00Z";
  next.complete=false;next.prs[0].complete=false;next.prs[0].comments=[];
  const comparison=compareCaptures(old,next)!;
  expect(comparison.complete).toBe(false);
  expect(comparison.sources.filter(item=>item.kind==="missing")).toHaveLength(old.prs[0].comments.length);
  expect(comparison.states).toHaveLength(0);
});
