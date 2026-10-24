# Final browser and lifecycle audit — 24 October 2026

The interface tested was the compact build at source commit `c49f420` and its corresponding public replay.

## Observed in the browser

- Local workbench inspected at 1280 × 900 and 320 × 740. Expanded original evidence and mobile detail measured document/viewport widths 320/320. The public replay full Sources view also measured 320/320.
- A real service stop caused a note save to fail visibly without clearing the draft. Dismissing the error retained Retry connection. After restart, Retry connection restored availability and Save note succeeded. The temporary note was cleared and saved afterward.
- Saved analyses closed with Escape and returned focus to its trigger. With reviewed cards excluded, marking the selected Eventyay card reviewed moved mobile detail focus to the next card heading. The temporary reviewed marker was reopened afterward.
- Fresh public GitHub import of `fossasia/eventyay#6104`: nine sources, five human inputs, four automated entries. Actual local Gemma returned one possible request/response pair, about 4.0 seconds recorded runtime. Its meaning remained explicitly unverified.
- Download review sheet produced `reviewradar-ff4652272d62.md`. The downloaded file was read back: source dates, scope, coverage, original links, quoted evidence and the distinction between a response and a verified fix were present.
- Current public replay rendered as Historical replay, without live import/inference controls. Deliberately incomplete coverage remained visible. No warning/error console entries were returned for the inspected replay session.

Screenshots are retained under ignored `outputs/final-desktop-audit.jpg` and `outputs/final-mobile-audit.jpg`. Temporary viewport overrides were reset.

## Service lifecycle correction

macOS logs showed Dock removing both ChatGPT-attributed ReviewRadar jobs when ChatGPT quit. PID 1 and KeepAlive did not prove survival of that event. The prior independence claim is withdrawn.

Start/Stop launchers operate only on exact project-owned jobs. Start is intended to be opened by the user through Finder/Terminal and restarts existing owned jobs rather than retaining their attribution. Saved database records persist; an in-flight import/analysis can be interrupted. Preflight checks saved configuration and required paths before stopping jobs; model checksum verification still occurs during startup.

**The user-launched path has not passed an actual ChatGPT-quit survival test.** Current services launched from this chat remain subject to the observed attribution behavior. No login-startup item is installed or unrelated service stopped.

## Limits

These observations do not certify every keyboard path, full screen-reader interaction, actual reduced-motion rendering or arbitrary source content. Reduced-motion CSS was inspected, without an OS-preference trial. No genuine external contributor trial or measured human saving has occurred. Semantic model errors remain possible. Week 3 publication still needs its separate factual and eligibility/rights/rules gates.

## Final launcher validation and draft

After the preflight change, the complete Python suite passed: **136 tests and 34 subtests**, including 26 lifecycle checks. Ruff F/E9, shell syntax and whitespace checks passed. The real read-only preflight reported valid prerequisite paths and services_changed false. No launcher restart was executed through Finder/Terminal. Previously passed 48 local frontend and three replay tests remain applicable because no frontend code changed in this follow-up. The existing Starlette/httpx deprecation warning remains.

DEV draft **7322997** was saved and visibly marked Unpublished Post, with devchallenge/hf26challenge/opensource/ai tags and Fully Autonomous article disclosure. It lists Overall and Best Use of Gemma. No Week 3 agreement was accepted and Publish was not clicked. The preview token is not stored in the repository.

## Publication follow-up

The separate user agreement was subsequently received and existing article 7322997 was published on 24 October, 09:29:13 UTC: https://dev.to/yashanand69/reviewradar-the-request-a-possible-reply-and-a-calmer-review-session-486. The browser showed Posted on 24 Oct and the Week 3 banner; the Unpublished Post notice was absent. Required tags, human-role/AI disclosure, Overall/Gemma categories and demo/source links were retained. Publication proof is stored under ignored outputs/week3-publication-proof.jpg. This supersedes only the earlier pending-publication status; technical and user-validation limits remain.
