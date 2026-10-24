---
title: "ReviewRadar: the request, a possible reply, and a calmer review session"
published: true
canonical_url: https://dev.to/yashanand69/reviewradar-the-request-a-possible-reply-and-a-calmer-review-session-486
tags: devchallenge, hf26challenge, opensource, ai
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 3: Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19).*

## What I Built

**ReviewRadar prepares a source-linked reading sheet for public pull requests you authored.** Local Gemma proposes individual reviewer requests and possible later author replies. You compare the exact passages, inspect the surrounding discussion, and save your own decision. GitHub stays unchanged.

For **Slow and Steady**, the small chore is recovering context before you resume a review session, rather than keeping another inbox under constant watch.

The intended user is an open-source contributor returning to several conversations after a break. A PR label tells you its state; it does not reconstruct which particular question a later update might answer. ReviewRadar's hypothesis is that preparing those pairs can reduce repeated searching. Whether the preparation and correction cost actually saves someone effort remains unproven.

My own contribution history supplied the problem. In [Eventyay #6104](https://github.com/fossasia/eventyay/pull/6104), a reviewer requested screenshots or a video and a later author update reported screenshots. Reading those together helps me decide what to inspect next. It does not prove the screenshots met the request or that the reviewer was satisfied.

Three things remain separate: GitHub's state at capture time, the model's suggestion, and your local judgment. The app does not write replies, resolve threads, verify code fixes or certify that a queue is complete.

## Demo

[Open the public historical replay](https://yashanand69.github.io/reviewradar/).

**This is saved evidence and saved model output, not online inference or a live inbox.** Choose **Original example** or **Mixed evidence example**, then open it. Decisions stay in your browser; switching examples runs no model. Both examples disclose their source scope and capture dates.

Try this short workflow:

1. Open the original Eventyay example and compare the reviewer passage with the possible author response. Expand the full comments or follow their GitHub links.
2. Add a note describing your next inspection. Save it, mark reviewed locally, then reopen it. Those are reversible local choices.
3. Open the mixed Visdom #1919 example. Its proposed response is weak: a test-pass statement does not explain whether the requested warning was retained. Choose **Reply not relevant**, save that assessment, and download the review sheet.

Disagreement does not hide the card, rewrite the model output or mark it reviewed. **Not a request** records an extraction disagreement; **No disagreement recorded** clears either assessment. Notes and review status remain independent.

The mixed example retains an actual v13 run, including its omitted branch-update request and insufficient response. Nine human source bodies are retained; automated entries are omitted, so this demonstration is visibly incomplete. It is a separate curated-input run, not the full evaluation replayed under a different label. The original v9 example is unchanged.

For fresh intake and inference, [run the local application](https://github.com/YashAnand69/reviewradar#run-locally). It supports one to five selected public PRs authored by the chosen account. The pinned model download is approximately **2.84 GB**, plus runtime and application dependencies. A no-model chronology reading list is available without weights.

![Agent-operated local demonstration: a saved disagreement and next inspection note, separate from the unchanged model output](https://yashanand69.github.io/reviewradar/mixed-assessment.jpg)

[Read the actual exported inspection sheet](https://yashanand69.github.io/reviewradar/example-review-sheet.md). The screenshot and sheet come from an agent-operated demonstration, not an external participant trial. The saved sheet keeps the weak prediction alongside the disagreement; it does not silently repair the prediction.

## Code

[Source, setup, model manifest and tests](https://github.com/YashAnand69/reviewradar).

Application code is MIT licensed. Model/runtime dependencies and attributed third-party discussion text retain their own terms and rights. Our application license does not relicense other people's comments.

## How I Built It

React and TypeScript provide the workbench. A local FastAPI backend imports discussions through the GitHub CLI, validates immutable snapshots and keeps analyses separately from local decisions in SQLite. Gemma 4 E2B runs through a pinned llama.cpp service on loopback. There is no hosted inference dependency or GitHub credential in the browser.

The model has two bounded jobs: identify distinct human-reviewer asks, then propose relevant strictly later author passages. Source passages receive keys; the model selects keys and the application reconstructs the exact text. Local validation rejects ineligible reviewer passages and mechanically invalid source relationships. Both generation stages check the actual templated token budget; oversized conversations fail visibly instead of being silently truncated.

This architecture came from failures. Early outputs treated author updates and approvals as requests; another changed punctuation while quoting. Passage selection fixes the quotation problem, not the language-understanding problem. Later experiments still missed real asks and matched weak replies.

The alternative is deliberately simple: a chronological list of human reviewer comments. You identify asks and search subsequent author updates yourself. Gemma adds semantic extraction and proposed association; that is its substantive role. When those suggestions are wrong, Sources and the baseline remain available. Baseline mode has no model-disagreement selector, and switching to it is explicit.

The interface now puts a neutral description above a collapsed **Unverified model explanation**. Historical rationale remains intact, including overconfident wording. A human assessment is exported separately, rather than quietly converting a bad prediction into a success.

## What the Checks Showed

The [evaluation report](https://github.com/YashAnand69/reviewradar/blob/main/evaluation/REPORT.md) retains the original pilot, fresh v10 cases, v11 experiments, a rejected v12 experiment and the frozen v13 final test. These are assistant-labelled engineering studies, not independent customer ground truth or random samples.

In the [final six-PR evaluation](https://github.com/YashAnand69/reviewradar/blob/main/evaluation/v13-final/REPORT.md), eight asks were labelled before inference. Five were covered and three missed. Five output cards included one duplicate; one matched card selected insufficient generic test-pass evidence. A compound card represented two genuine asks. Two no-ask bot-invocation cases correctly produced zero cards. The frozen v13 implementation was preserved; later v14/v15 experiments are reported separately and rejected as release defaults.

A later focused-comment v14 revision recovered all eight actions on those now-exposed cases; a separate frozen set covered six of six with two duplicates. It still produced considerable noise on larger discussions and missed five of eight actions on another exposed set. Both this focused revision and an extra verification experiment remain archived rather than promoted; the app retains v13. A final fresh live Eventyay #6104 check also returned zero cards with v13, failing the request-card smoke assertion. Earlier passing runs do not override that failure. The [current reports](https://github.com/YashAnand69/reviewradar/blob/main/evaluation/REPORT.md) retain those unfavourable results too. The interface now exposes captured reviewer comments without a request card, so a user can inspect possible omissions; it does not certify complete coverage.

Those denominators matter. Fewer cards can conceal missed work: v12 was rejected after substantial recall loss. Passing exact-source checks cannot establish relevance. Most final cases came from one project and one contributor's history; we do not generalize these results into a reliability percentage.

The recorded engineering checks now include the focused-model, source-inspection, local-only trial and foreground-lifecycle regressions, alongside type checks. Exact version-specific counts are retained in the release record. These protect source boundaries, migration, recovery and interface behavior; they are not model-accuracy or human-productivity evidence. SQLite migration was rehearsed against a consistent backup before upgrading stored decisions. In-flight save guards prevent duplicate submissions when navigating away and back.

Earlier released views received bounded browser checks covering desktop and 320 px layouts, keyboard focus and a failed save followed by reconnection without losing the draft. The new source-inspection panel and trial guide do not yet have a current rendered-browser pass because browser control is disabled. An emulated reduced-motion preference was checked; a full screen-reader audit was not. Unsaved drafts survive navigation in the open tab, not closing or reloading it.

The Mac launcher now keeps a dedicated foreground Terminal session. An actual agent-started check reached readiness, cleaned its owned children and preserved saved data. The user-started path has not yet been verified through quitting ChatGPT. This is a local application, not an always-on hosted service. Startup success is not evidence of that lifecycle test.

## Why Does Open Innovation Matter?

Open weights and an inspectable runtime let us preserve dated inputs, examine prompts and source rules, reproduce a failure and replace the model independently of a hosted API. Gemma performs the central interpretation rather than serving as decorative branding.

The [Gemma artifact](https://huggingface.co/ggml-org/gemma-4-E2B-it-GGUF) and [llama.cpp](https://github.com/ggml-org/llama.cpp) are pinned in the repository manifest. Processing saved discussions can run offline after installation. Fresh GitHub imports and initial downloads still require internet; local inference still costs memory, electricity and setup time.

## The Human Role

I supplied my actual contribution history, chose this project from the researched ideas and asked for staged implementation, critical reviews and explicit treatment of failures. Eventyay #6104 and Visdom #1919 make the problem concrete in work associated with my account. These are substantiated inputs, not an invented customer story.

AI agents contributed substantially to research, design, implementation, tests and this article. I am not claiming manually written code or independent participant validation. During use, a person still reads the sources, records disagreement and decides what to do next.

A [public trial request](https://github.com/YashAnand69/reviewradar/issues/1) had zero comments at the last check on 24 October. We have no genuine trial or measured time saving. A [local-only trial guide](https://yashanand69.github.io/reviewradar/trial.html) now prepares feedback without uploading answers automatically. The next product question is whether contributors find the prepared sheet worth its installation and correction costs.

## Prize Categories

**Overall** and **Best Use of Gemma**. This entry uses local Gemma for actual request extraction and response association. It claims no category for unused integrations.
