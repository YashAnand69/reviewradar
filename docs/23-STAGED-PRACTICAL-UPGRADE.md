# Practical upgrade, after the Week 3 submission cutoff

The submitted source is `d264d9ff496c11566e74ab6ae8f1273039a2a089`. The official cutoff was 26 October 2026 at 12:29 IST. Work here is a follow-up on `improve/daily-use-followup`, not represented as work completed within the contest period. The published entry and replay remain preserved.

## Stage 1 — Model reliability

Run a frozen, bounded candidate against the exposed 20-PR regression set, keep predictions and compare semantic failures. v17 isolated each reviewer comment, recovered previously missed asks but introduced false tasks and weak matches. It is not promoted. The active v13 model still requires source inspection. Independent review and a fresh, independently labelled evaluation remain necessary before promotion; a green mechanical test is insufficient.

## Stage 2 — Return to regular work

Save up to five selections, each containing up to five authored public PR URLs. Browser storage contains account/URLs and the last capture ID; comments and credentials are not copied into it. Opening a selection retrieves its earlier immutable capture and prefills an explicit import. No background network requests are added.

After successful import, compare exact captured content: new/edited reviewer comments, author updates, automated sources, title/state/head changes and sources absent from the new capture. Absence is not described as deletion. Incomplete capture warnings remain visible. New captures keep independent notes and review decisions. A failed fetch leaves the old reading intact. Missing/edited content is evidence to inspect, never proof a request was fulfilled.

Acceptance: validated stored selection data, no foreign URL acceptance, unrelated/backwards capture rejection, browser storage failure message, old-note retention, no model run or GitHub write from checking a saved selection.

## Stage 3 — Setup and recovery

`scripts/doctor.py` checks installed dependencies, built assets and optional tools offline. Optional artifact hashes establish file identity only. It prints actions without credential contents or configured private paths. `Start Reading.command` starts the local app without starting/downloading a model or stopping any service. First-time Python/dependency installation is still required. Live GitHub import still requires CLI authentication and internet; saved-source reading does not.

Acceptance: missing dependencies/assets fail clearly, a valid baseline needs neither Node nor model weights at runtime, wrong model hash is reported, model/runtime binaries are not executed by diagnosis. An actual independent Terminal launch and quit-survival test remain separate from code tests.

## Stage 4 — Usability and real evidence

Use the paired protocol in `24-COMPARATIVE-TRIAL.md`. Record all attempts, familiarities, task order, errors, preparation and correction time. Agent exercises are engineering evidence only. No participant has completed this protocol yet. No messages or extra recruitment were sent in this follow-up.

## Stage 5 — Review and release gate

Review the combined code and rendered flows, including refresh failure, storage failures, source differences, public replay separation and narrow layouts. Subagents began the stages but reached an account usage limit before independent review. Parent completion/testing is not relabelled as independent review. Keep this work on the follow-up branch until that gate passes. Do not overwrite the deadline submission or imply post-cutoff work was evaluated by contest judges.

## Verification checkpoint

- Full backend suite: 178 tests and 34 subtests passed, with the existing Starlette/httpx deprecation warning. Four setup-diagnosis tests cover absent environment, model-free source reading, missing assets/dependency mismatch, and artifact rejection without executing the model runtime.
- All 78 local frontend tests and the six dedicated replay tests passed; TypeScript/build and focused lint passed. Local frontend DOM tests cover explicit saved-selection confirmation, changed reviewer evidence and no implicit inference or GitHub writes, alongside existing failed-refresh/note-retention regressions. These are not rendered-browser proof.
- A broad replay-mode test invocation incorrectly included local-only app tests, which expect controls intentionally absent from replay. Those failures are retained in the operation record; the dedicated replay suite is run separately using the existing intended split.
- Doctor verified the actual pinned model/runtime checksums without starting or stopping them. A baseline launcher syntax check passed. No fresh-machine or independent ChatGPT-quit test is claimed.
- The Mac is locked and browser access disabled. The user has been asked to unlock/enable access. No bypass or fabricated screenshots are used. Independent agent review is pending because the agents reached the account usage limit.
