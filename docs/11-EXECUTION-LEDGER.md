# ReviewRadar execution ledger

Started 23 October 2026. Only verified results belong here. Plans remain in the numbered specification documents.

## Stage 0 — planning and independent audit

Three agents drafted product/UI, technical/evaluation/privacy and delivery/rules documents. Cross-review identified scope contradictions, ambiguous completeness, conflicting acceptance IDs and model context values. The parent integrated corrections in `10-PLANNING-AUDIT.md` and the authoritative contract.

**Status:** initial plan accepted for implementation. This is not application acceptance or contest certification.

## Stage 1 — real data and model development proof

Read-only fresh probes retrieved Eventyay #6104, Visdom #1864/#1872 and VoxBento #718, including general comments, reviews and inline comments. These probes are not the final importer or coverage proof. A new authenticated loopback model process was started on a distinct port, without stopping another application. The runtime reported Gemma 4 E2B Q4_0 and a 16,384-token context.

The first Eventyay development prompt failed semantically (author update, praise and empty approval emitted as requests). The revised structured/few-shot development prompt returned the genuine screenshots request and its later author reply. First/revised elapsed times were 10.31/8.07 seconds on this machine. This is a development observation, not held-out accuracy or human effort measurement. Both raw results are retained in ignored local outputs.

**Status:** enough proof to begin bounded engineering. Independent labels, strict runtime validation and final evaluation are pending.

## Stages 2–3 — implementation

Parallel ownership: backend/model/storage/API; read-only GitHub intake/provenance/labels; frontend/evidence workbench. Parent owns integration, setup, review, release and publication. No PR, GitHub write or DEV publication has been performed by this project so far.

**Status:** in progress.

## Remaining gates

- Full local import → model/baseline → evidence → decision → export flow.
- Regression, adversarial, persistence, responsive and accessibility checks.
- Frozen independent evaluation and honest error report.
- Clean install, provenance, secret scan, public replay and actual inference demonstration.
- Claim-audited submission draft and final Week 3 eligibility/rights/rules confirmation before publication.
- Genuine-person trial remains **not conducted**. No human savings claim is available.

## Integrated working preview — 23 October

Stages 2–3 implemented: read-only GitHub intake, strict source schemas/hash, local two-stage Gemma processing, chronology baseline, SQLite, history, local disposition/notes, source reading and JSON/Markdown downloads. Browser-facing source text is escaped. Import/model limits are visible per PR. The interface uses separate local/replay adapters and restrained reduced-motion-aware transitions.

Independent intake and adversarial tests were reproduced by the parent. Later integration found/fixed model-written quote errors, repeated response enumeration, temporally invalid choices, quoted-source duplication, small operational typography, modal error placement, draft-note loss, reset state and a late-save race across analyses. Request edits after a reply now receive a source-history caution. These fixes are engineering findings, not a claim that all possible mistakes have been eliminated.

Final local verification: **73 backend tests, 24 local frontend tests, three separately run replay tests**; Ruff F/E9, TypeScript and Vite build passed. npm audit reported zero known vulnerabilities after upgrading vulnerable Vite/Vitest dependencies. Python TestClient emits a dependency deprecation warning; it is not hidden or represented as a test failure. The actual local API smoke path imported a fresh public Eventyay PR, performed real Gemma inference, saved/reopened a local decision, exported and restored results without a GitHub mutation.

A clean source archive at 9ef27f7 installed all locked dependencies and started on a separate loopback port. It loaded the sample and ran a baseline without a configured model. The temporary server was stopped. The canonical full app remains at http://127.0.0.1:8893/. This is clean setup/startup evidence on the named Mac, not a cross-device/browser guarantee.

## Evaluation gate

Seven engineering-labelled requests across four real PRs. Development v8 found four of four. The untouched v8 holdout found three labelled requests plus one quoted duplicate. The informed v9 change excludes quoted-only passages; its rerun is explicitly a regression, not a fresh holdout. It still emits additional agreement as a possible ask. No labels were silently rewritten to improve the count. See evaluation/REPORT.md and results-summary.json. No human trial, testimonial or human effort percentage exists.

## Source and preview release

Public repository: https://github.com/YashAnand69/reviewradar . The first Linux CI run passed at https://github.com/YashAnand69/reviewradar/actions/runs/39928528875 . Public preview: https://yashanand69.github.io/reviewradar/ . Page/assets/sample JSON were HTTP-verified; replay DOM tests verified no local API connection, browser-local decisions/reset and honest sample-failure handling. The sample is an actual saved v9 API result with three evidence pairs; deliberately incomplete and historical. It is not hosted live inference.

## Remaining gates and publication status

The browser tool reports **local browser use disabled in Work settings**. The user was asked to enable access; no reply has been received. Rendered visual, keyboard-only, mobile-overflow, reduced-motion and screen-reader checks remain unverified. Delegated agents hit an account usage limit; the parent finished integration, and no blanket independent final sign-off is claimed.

A full template-aligned local DEV draft exists at docs/DEV-SUBMISSION-DRAFT.md with code/demo/evaluation links and truthful AI/human-role disclosure. It is **not published** and no external DEV draft was saved. Final browser verification and action-time Week 3 eligibility/rights/rules confirmation are still needed before the single contest entry is published. Earlier challenge agreements do not substitute for that confirmation. Deadline: 26 October 2026 at 12:29 p.m. IST.

Planning/audit is complete; the local full-stack/public preview release is working and tested within the described limits. The contest-submission stage is incomplete.

## Follow-up issue audit and fixes — 23 October, evening

See `15-FOLLOW-UP-AUDIT.md` for reproduced findings and exact browser limits. Two agents reviewed and repaired the backend/interface; a third independently reviewed the settled diff. Fixed quoted-context request/reply eligibility, unknown pagination completeness, malformed external-data failures, replay export edit-history/rejected-card warnings, mixed-timezone timeline ordering, mobile fallback focus and asynchronous history-dialog return focus. The model protocol is now v10; the public historical sample correctly remains its saved v9 result.

Parent verification: **98 backend tests + 34 subtests, 33 local frontend tests + 3 replay tests**, Ruff F/E9, TypeScript, production build and diff whitespace checks passed. A restarted app performed fresh public intake and real v10 inference (one pair, 4.281 seconds), persistence/reopen, source-bound retrieval and export. No GitHub discussions or upstream code were changed. Existing dependency deprecation warning remains documented.

Browser access temporarily worked: sample, desktop/320px evidence, local note/reopen, fresh GitHub import and Gemma result, saved-history keyboard behavior and the public historical replay were inspected. Two focus defects were reproduced. Access then became disabled again, so the corrected build has **not** received a rendered retest. No full keyboard-only, screen-reader or reduced-motion completion is claimed. No human trial has occurred and no Week 3 DEV post has been published.

## Service lifetime and practical-use completion — 24 October

The user's repeated “action did not finish” report exposed a delivery defect: terminal-bound app/model processes had stopped while the browser retained the interface. Replaced that lifetime with project-scoped macOS login-session services (no login-startup installation), explicit start/status/stop, real model readiness and recoverable browser sessions. The frontend keeps open drafts/evidence, offers persistent reconnect after dismissal, renews once on a rejected token, and never automatically repeats a write/model call after a network failure. Source reading/baseline remain available when the model is offline.

A real stop/start exercise found two additional lifecycle issues: TIME_WAIT sockets misidentified as unmanaged ports and asynchronous teardown leaving stale service records. Both were corrected and tested; the final real recovery run passed. Exact source/decision persistence and actual frontend API token renewal/save/export were verified against restarted managed services. See `16-RELIABILITY-AND-PRACTICAL-USE.md`.

Final checks: **130 Python tests + 34 subtests; 48 local frontend tests + 3 replay tests**; Ruff F/E9, TypeScript/build, diff checks and npm audit (zero known vulnerabilities) passed. Current bundle built under Node 24.22.1; prior CI/setup pin remains 24.19.0. The dependency TestClient deprecation warning remains documented.

Practical improvements include a concise sample walkthrough, a next-action note prompt, clearer unverified-interpretation framing, and a smaller header after sources load so working evidence receives more space. The submission draft explains the actual contributor task, baseline versus semantic extraction, setup cost, recovery failure/fix, and human input truthfully. `17-DEMO-AND-TRIAL.md` provides a real-app recording script and consent-aware volunteer invitation; no outreach, trial or recording has been claimed.

The parent completed keyboard-driven real import and model analysis while browser access worked. Access became disabled again before the final compact-header/mobile/recovery render checks; an enable-access question is pending. The final DEV post is still unpublished and Week 3 eligibility/rights/rules confirmation remains required at publication.
