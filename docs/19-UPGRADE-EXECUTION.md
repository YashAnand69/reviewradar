# Evidence and usability upgrade execution

Started 24 October 2026. See the staged plan in the local outputs directory. This ledger records actual observations, not promises of a prize.

## Stage 0 — baseline and recovery checkpoint

- Source baseline: `0617c84cb3a4b201ba527573c56fb0bf9498c51f`; isolated branch `improve-review-evidence`; initial tree clean.
- Consistent SQLite backup made with SQLite backup API in ignored `outputs/upgrade/pre-upgrade.sqlite3`, integrity_check `ok`, schema user_version 0, 10 snapshots / 13 analyses / 4 local dispositions. Backup private and uncommitted. Restore requires preserving subsequent decisions and compatible code.
- Existing backend suite: 136 tests and 34 subtests passed; existing Starlette/httpx warning retained.
- Model implementation hash `7df9cce236cfddccfbb37ee710397e31853a35cd70956b754b16ba05ecc75367` retained; no semantic tuning authorized on fresh evaluation cases.
- Current-status browser-retest wording reconciled in evaluation report and trial/demo guide; historical v8/v9 results unchanged.
- API contract for additive local assessment: unassessed / not_a_request / reply_not_relevant, independent from review state and note. Missing legacy field preserves existing assessment; explicit unassessed clears it. Reply feedback requires a proposed response; model-specific assessment is unavailable in baseline mode. No GitHub writes, automatic hiding or evidence rewriting.

Stage 0 review: baseline backup readable and existing tests pass. The user-started launch/ChatGPT-quit test remains outstanding. Technical workers have separate backend/frontend/evaluation ownership.

## Stages 1–2 — evidence and bounded experiments

- v10: eight fresh PRs, 18 assistant labels, 16 full / one partial / one missed; four duplicate and five non-ask extras. Parent reviewed difficult source/scoring cases and the separate legitimate response-ID addendum. Engineering review, not independent human adjudication.
- v11 development improved a specific test-location response. Separate six-PR set still emitted three approval/thanks tasks and selected one acknowledgement-only reply.
- v12 explicit empty-output examples lost eight genuine asks: rejected, with first attempts preserved.
- v13 restores v11 instructions, retains narrow whole-ack exclusion, adds reviewer context and local eligible non-bot reviewer checks. Mixed-PR regression rejects approval/author/bot/quoted-only runtime bypasses.
- v13 frozen before next six source discussions inspected; labels frozen before predictions. Five of eight asks covered, three missed, one duplicated rationale, one insufficient generic-test response. No subsequent tuning. All candidate reports independently reviewed by agents; not an independent human trial.

## Stage 3 — local decisions, migration and recovery

- Atomic schema-1 migration rehearsed twice; original ten snapshots, thirteen analyses and four dispositions preserved. Actual private DB migrated after rehearsal, integrity checked. Omitted legacy assessment preserves; explicit unassessed resets. Future/corrupt markers reject.
- Not a request / Reply not relevant remain independent of reviewed state/note; no hiding or GitHub writes. Baseline excludes model feedback; response feedback requires response. Immutable original analysis preserved, exports label local assessment and unverified explanation.
- Drafts keyed by analysis/card survive navigation. Pending-save guard prevents duplicate/out-of-order saves through remounts.
- Actual browser: stopped app only, attempted note+assessment save; visible failure retained both. Restarted app while leaving model running; Retry connection then explicit save succeeded. Original demo decision restored afterward; its timestamp changed by this disclosed test.
- Browser 320px: no overflow, native select/note focus visible. Emulated reduced motion returned zero transition/animation and was reset. Not a full screen-reader or OS-preference audit.

## Stage 4 — trial and lifecycle

One authorized request: https://github.com/YashAnand69/reviewradar/issues/1. Latest check open, zero comments. No genuine trial or savings. User-run launcher exists; actual user-start then ChatGPT-quit survival test remains outstanding. No startup item or unrelated service changed.

## Stages 5–7 — release checks in progress

Original v9 example retained; fixed allowlisted mixed example preserves a separate actual v13 run and explicit omitted-source warnings. Full backend: 152 tests and 34 subtests passed. Initial direct pytest invocation had import-path collection errors; documented python -m pytest rerun passed. Existing Starlette/httpx warning remains. Frontend agent: 59 local + six replay tests, TypeScript passed. Final build/browser/deployment evidence follows when verified.

### Final local integration evidence

Independent review verified all nine retained mixed-example human source objects exactly match capture, all nine omitted automated entries are disclosed, model output equals its actual run, and v13 frozen hash is unchanged. Allowlisted sample routes passed validation tests. Actual browser opened both variants without inference. The mixed example saved Reply not relevant plus a next-inspection note; downloaded sheet `reviewradar-3c46c52d0010.md` was read back and contains source dates/links, uncertainty, incomplete coverage, original output and separate local assessment. A copy and genuine local screenshot are bundled for the demo. This is agent-operated demonstration evidence. Screen recording attempts were too brief/interrupted to publish as a full walkthrough; none is claimed.

Local tests: 59 passed, six replay-mode tests separately passed; local/replay builds and dependency audit pass, zero npm vulnerabilities. Static source wording now says captured conversation rather than implying every GitHub entry was fetched. Final deployment/post verification follows after publication.

### Deployed and existing entry updated

- Source upgrade81b4020f830e21d06ec5c5c9b2a3e7c99b7cf597 pushed; Linux CI40115857224 success. Pagesa5fa3a73bcadddb6649b80a50e3708edf4b53bdf deployed, run40115889943 success. Eight files include mixed JSON, actual export and screenshot. Public response bytes match built artifacts.
- Actual public browser loaded mixed example with correct nine human sources, capture/analysis dates and incomplete warnings. At320px detail documentwidth305≤viewport320; override reset. Replay has no live-import/model controls.
- Existing published DEVarticle7322997 saved with revised workflow, genuine screenshot, exported artifact, human-role/AI disclosure, Overall+Gemma and honest evaluation results. Public page/banners/tags verified; embedded screenshot loaded at800px. No new entry or new legal acceptance.
- Latest feedback request check: open, zero comments. Local app+model healthy. Outstanding: semantic reliability, genuine external trial, complete recording and user-started quit survival. The interactive demo is delivered; none of these outstanding items is falsely marked complete.

Final factual record written 2026-10-24T17:28:15.240124+00:00. Publication proof retained privately in outputs/upgrade/dev-updated-proof.jpg.
