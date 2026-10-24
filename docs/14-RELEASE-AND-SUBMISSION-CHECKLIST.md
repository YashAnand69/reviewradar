# Release and Week 3 publication checklist

23 October 2026. The local application is released with documented limits; the public site is a historical replay. The [Week 3 entry](https://dev.to/yashanand69/reviewradar-the-request-a-possible-reply-and-a-calmer-review-session-486) was published on 24 October 2026 at 09:29:13 UTC (14:59:13 IST). Publication is not a judging or prize decision.

## Verified links and environment

- Source: https://github.com/YashAnand69/reviewradar
- Historical public preview: https://yashanand69.github.io/reviewradar/
- Local full app: http://127.0.0.1:8893/
- Verified Linux CI checkpoint: https://github.com/YashAnand69/reviewradar/actions/runs/39928528875
- Tested local environment: macOS 27.0.1 arm64, Python 3.12.13, Node 24.19.0, 24 GiB RAM.
- Model: pinned Gemma 4 E2B Q4_0, pinned llama.cpp artifact/source archive, 16,384-token configured context. Model license and source attributions are separate from the application MIT license.

The public preview returns the saved v9 analysis with ID `cd37e8a309fb4561b537e2043d5bc93d`, bound to snapshot `dedb833f52b2271399b790c12483dfaf1afb293953cf86b9fa452116eae601dc`. It contains three request/response pairs from six deliberately selected sources. Completeness remains false. No live GitHub import or inference is advertised on that public page.

## Completed engineering evidence

- [x] Fresh project and repository created during the Week 3 window.
- [x] PRD, TRD, UI essentials, evaluation, privacy, essential skills/runbook, stages and acceptance matrix drafted and cross-audited.
- [x] Public-only, authored-PR intake covers general comments, reviews and inline/thread pagination with visible bounds.
- [x] Actual local model inference performs request extraction and possible-response selection; exact text is reconstructed from source passage keys.
- [x] Local persistence, history, reviewed/reopen, notes, source JSON and Markdown export implemented.
- [x] Per-PR failure, overflow and incomplete-source states remain visible; no silent model/baseline fallback.
- [x] Backend and UI tests, source formatting, type/build checks and current dependency audit pass at the recorded checkpoints.
- [x] Frozen development/holdout pilot retained, including the quoted-duplicate failure and honestly relabelled regression.
- [x] Source scan excludes credentials, weights, runtime binaries, local SQLite and full raw discussion histories.
- [x] Clean source archive setup and startup verified; baseline works without model configuration.
- [x] Actual managed macOS service stop/start, immutable source/decision restoration and frontend API session-renewal/save/export verified.
- [x] Real model readiness, actionable reconnect and persistent retry implemented and regression-tested.
- [x] Public replay deployment and saved JSON/assets verified by HTTP; local/replay adapter behavior checked in DOM tests.

## Required before calling the entry submission-ready

- [x] Rendered desktop and 320px inspection, expanded evidence and full Sources; no page overflow in inspected views. See `18-FINAL-BROWSER-AND-LIFECYCLE-AUDIT.md`.
- [ ] Keyboard-only completion, visible focus, dialog return focus, reduced motion and meaningful error announcements.
- [x] Existing public historical preview rendered in a separate tab without a privileged GitHub page/API session. Corrected replay retested at desktop and 320px.
- [x] Independent follow-up backend/frontend audit and third-agent final-diff review completed; confirmed findings received regression fixes. See `15-FOLLOW-UP-AUDIT.md`.
- [x] Final draft claims checked against the inspected release and Week 3/general rules on 24 October. No fabricated human-feedback or measured-savings statement is present. The saved DEV draft remains unpublished.
- [x] User confirmed Week 3 eligibility, material rights and acceptance of Week 3/general rules, including promotional reuse, in the action-time reply before publication.
- [x] Published the existing DEV article 7322997 once, with devchallenge/hf26challenge/opensource/ai, Fully Autonomous disclosure, Overall and Best Use of Gemma. Verified posted time, public canonical URL, Week 3 banner, demo/source links and absence of the unpublished notice.

Initial browser checks became available and are recorded in `15-FOLLOW-UP-AUDIT.md`. They exposed focus defects now fixed in code and DOM regression tests. Browser access then became disabled again before the corrected build could be rendered. Browser access later recovered. Corrected-build visual, mobile fallback focus, history Escape/return focus, actual service recovery, fresh import/model result and download were checked. Full screen-reader and actual reduced-motion preference testing remain unverified. User-launched service survival remains outstanding. See the final browser audit.

## Optional evidence that must not be fabricated

- Genuine contributor trial using `09-TRIAL-GUIDE.md`.
- Actual human reading/correction timings and willingness to use again.
- A recording of the running local model/UI, if browser access permits. The rules accept a deployed demo or video; a recording is useful evidence, not a mandatory extra category.

No participant trial has happened. The draft therefore makes no human savings percentage or testimonial claim. The engineering pilot still finds an extra agreement/observation as a possible ask; the source is exposed, and that limitation stays in the report.

## Publication boundary

Official cutoff: **26 October 2026 at 12:29 p.m. IST** (25 October at 11:59 p.m. PDT). Recheck the [Week 3 page](https://dev.to/challenges/hacktoberfest-week3-2026-10-19), [Week 3 rules](https://dev.to/page/hacktoberfest-week3-2026-10-19-contest-rules) and [general rules](https://dev.to/page/official-hackathon-rules) at publication. Writing is the most heavily weighted criterion; no numeric weights or winning probability are invented here.

The separate Week 3 agreement was confirmed by the user before publication. Published article: https://dev.to/yashanand69/reviewradar-the-request-a-possible-reply-and-a-calmer-review-session-486. Source release at submission: `48f40baea2f66e12751d8a650286078f67faa15d`; public replay commit: `c671ff268f730508552db0da08c46aee51038c53`. Any subsequent changes must retain their actual dates and scope. No duplicate entry was created. The prior private preview token is not retained in source.
