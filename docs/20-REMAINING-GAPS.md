# Three remaining gaps: action and verified status

Later same-day daily-use changes and current verification are recorded in [the daily-use upgrade](21-DAILY-USE-UPGRADE.md). Counts and checkpoints below remain dated earlier observations, not the latest release totals.

25 October 2026 (Asia/Kolkata). This is a factual release record, not a declaration of perfection or a predicted judging outcome.

## 1. Missed requests and misleading matches

The archived v14 experiment examines each eligible reviewer comment independently while retaining full reviewer context. Selection remains source-bound; source text is untrusted. More than 12 eligible comments, 40 candidate requests, token overflow or failure rejects the affected PR visibly. The shared 90-second budget is cooperative around HTTP operations and streamed chunks, not an operating-system hard deadline.

On the exposed cases containing the three original misses, v14 recovered all eight labelled actions (v13 found five). A separate frozen six-PR set covered six of six actions with two duplicate cards. That is a limited positive result, not a perfect classifier. The broader eight-PR regression emitted 31 cards, including four duplicates and eight non-request/context extras, plus two insufficient/wrong primary replies. A subsequent independent pool exposed five missed actions out of eight. A v15 verifier was tested and rejected: little noise reduction, retained misses, additional work. Original predictions and frozen annotations were preserved. See the evaluation index for every denominator and counter-reading.

The model-only panel **Reviewer comments without a request card** exposes exact retained human reviewer text with dates and original links. It may include approvals or context. A comment with a card can still have missed asks, so the panel does not prove coverage. It never adds model cards, marks obligations or changes GitHub. A person can inspect Sources, record disagreement and choose a next action.

Independent agent review checked local focus-key constraints, actor/quote/chronology boundaries, caps, failures and deadline handling. The archived candidate exactly matches frozen v14 hash `5f4eae1bdf0cc265d2ee16e71e3369c39f9f178cc31e7ac6457656ea7d05d2b1`. The shipped path remains v13, hash `24caf2b5b4713df24641ebf6c6b66b846e28893bf5aa5900ad66580530bcba47`. Both v14 and v15 are rejected as release defaults. No further semantic tuning follows this release decision.

A final fresh live Eventyay #6104 import returned zero cards with v14 and, after rollback and restart, with confirmed v13. The request-card smoke assertion failed. The captured screenshot/video request remains inspectable; the source panel does not cure this model omission. Earlier passing smoke results are not substituted for this failed current check.

## 2. Genuine tester feedback

Published [self-guided trial](https://yashanand69.github.io/reviewradar/trial.html): no sign-in, model download, private input or analytics. Answers remain in the tab. The participant explicitly prepares, edits, downloads or copies feedback and separately chooses whether to post it publicly. Quotation permission defaults to not granted; edited answers invalidate prepared feedback. The elapsed interval includes reading, pauses and writing and is not a time-saving measurement. Synthetic tests never count as feedback.

The single [GitHub recruitment request](https://github.com/YashAnand69/reviewradar/issues/1) was updated with the live guide. Latest check: zero comments. The user authorized one DEV invitation; it was [posted on 25 October](https://dev.to/yashanand69/comment/3ipm6) through the signed-in Safari session. The one author invitation is outreach, not genuine participant feedback. No duplicate issue, repeated maintainer ping, vote request, fabricated participant or testimonial was created. The prior DEV entry remains published; it is not claimed updated with these latest changes while browser access is unavailable.

Trial HTML/JS/CSS were deployed in Pages commit `3d7f10c1d22bda8536b802a880f8674cc730bf72` and verified HTTP 200 with exact built bytes and correct content types. Four synthetic form tests pass. The current trial's rendered browser check remains pending after browser control became disabled; earlier screenshots do not count as this check.

## 3. Startup and lifetime

New Start launcher preflights, stops only exact owned legacy jobs, then keeps a foreground supervisor in a dedicated Terminal. It creates and owns only its child process groups, uses explicit environment/private logs, refuses occupied unmanaged ports and cleans up on startup failure, child exit or Ctrl+C/SIGHUP/SIGTERM. Stop launcher does not search for stale PIDs or kill foreground sessions by port; use Ctrl+C in their own Terminal. No login startup, daemon or automatic restart is installed.

Thirty-nine lifecycle tests passed, including a real disposable wrapper/descendant cleanup test preserving an unrelated listener. An actual app/model foreground session reached readiness, cleaned both children on SIGINT, retained identical saved data and restored the prior legacy session. This actual check was agent-started and does not prove independence from the chat app.

**Independent start now observed on 25 October:** after the user reported starting the launcher, its foreground supervisor and children ran under a Terminal login session on `ttys002`. App/model endpoint checks and the saved-sample baseline save/reopen/export smoke passed. Legacy launchd jobs were absent. This verifies the separate start, not survival through quitting ChatGPT.

**Still requires the user:** keep that Terminal open, quit ChatGPT, and check the app in Safari/Chrome before reopening ChatGPT. This chat's native computer-control tool rejects Terminal access, so the agent cannot perform that independent UI step. The read-only `scripts/probe_local.py` can record endpoint samples in a second independent Terminal; its output alone does not certify that a quit occurred.

## Verification boundaries

The final retained code passed 165 Python tests and 34 subtests, 66 local frontend tests and six replay tests. Thirty-nine lifecycle tests are included in that backend count. Type/build and source formatting checks passed; the existing Starlette/httpx deprecation warning remains disclosed. The final **live model request-card smoke failed**, as described above; passing structural tests do not override that result. CI/deployment checkpoints are recorded in the execution ledger after release.

No genuine participant feedback, current rendered-browser pass, full screen-reader certification, exhaustive model recall or independent quit-test success is claimed. The DEV invitation is posted; the current trial/source-panel rendered audit and revised article update remain outstanding. The in-app browser connection was unavailable; Safari allowed posting before subsequent input was interrupted by user activity.

## Released checkpoint

Source `0f143c110e63d775795546b2840c0bc82297f170` passed [Linux CI](https://github.com/YashAnand69/reviewradar/actions/runs/40127077510). Pages `32e8cb038f358e547f07a1798a7e479af780a2bf` passed [deployment](https://github.com/YashAnand69/reviewradar/actions/runs/40127122147). Public index, JavaScript and trial assets returned 200 with exact built bytes and expected content types. The [public replay](https://yashanand69.github.io/reviewradar/) includes the source-inspection panel; it runs saved evidence, not hosted inference. Publication does not resolve the open limitations above.
