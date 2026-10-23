# Follow-up audit — 23 October 2026

## Scope

Two independent agents reviewed the interface and backend. The parent reproduced the main browser workflow and reviewed the proposed fixes; a third agent reviews the resulting diff. This report distinguishes completed observations from final-build checks that remain unavailable.

Story: select a public authored PR → read-only GitHub import → immutable local snapshot → local Gemma analysis → original request/possible response → reversible local decision and export.

## Confirmed findings

| Finding | Required correction |
| --- | --- |
| An author quoting a reviewer could be offered as the author's own response | Exclude quoted source spans from selectable request/response evidence and independently validate eligibility; retain the original text in Sources |
| Missing or non-boolean pagination flags could be treated as the end of a complete conversation | Require explicit pagination metadata at both top-level and nested connections; preserve visible incomplete coverage on failure |
| Null/non-object GitHub records and model choices could escape normal error handling | Validate external record/envelope shapes before dereferencing; retain valid source records and report failed/partial coverage |
| Replay Markdown export omitted the request-edited-after-reply caution | Include source creation/update dates and the same source-history caveat shown in the interface |
| Timeline sorting compared date strings rather than instants | Sort parsed timestamps, with a deterministic source-ID tie-break |
| Reviewing a card while reviewed items were excluded lost mobile keyboard focus | Follow the effective displayed card, including the empty-detail fallback |
| Closing asynchronously loaded saved history returned focus to the page body | Restore focus to the saved-history trigger explicitly |

The new model protocol is `human-review-passages-v10`. The public historical sample remains the actual saved **v9** result. Its recorded identity, runtime and date are not rewritten to suggest it ran under v10. Earlier evaluation counts remain evidence about their recorded versions, not a new v10 accuracy measurement.

## Browser evidence before access stopped

- Restored this project's loopback app and authenticated model service; the app's Retry connection recovered from the stopped server.
- Loaded the real historical sample with the persistent incomplete-source warning and expandable details.
- Inspected the evidence view at the existing narrow viewport and at **320 × 780**. The observed page width did not exceed the viewport. This was a bounded check, not a claim that every possible source body fits.
- Saved a note, selected another source, and observed persistence; reopened the test decision and cleared the test note afterward. No GitHub state changed.
- Reproduced the mobile filtered-card focus defect: the next evidence rendered, but focus fell to the body.
- Imported `fossasia/eventyay#6104` through the actual UI: nine sources, four automated sources explicitly excluded from the human queue.
- Ran actual local Gemma through that UI: one evidence pair, recorded runtime about **4.3 seconds** on this machine. This predates the v10 fixes and is not a benchmark or human time-saving measurement.
- Opened saved history, used Tab/Escape, and reproduced missing return focus. Dialog controls and source evidence were exposed in the accessibility tree.
- Opened the public GitHub Pages replay in a separate browser tab. It visibly identified itself as historical, disclaimed live import/inference and showed the sample's incompleteness. No privileged GitHub page or GitHub API session was needed to render it.
- The local page's captured warning/error console log was empty at the inspected model-result checkpoint.

After the user's continuation, the browser tool returned **“Local browser use is disabled in Work settings.”** The final corrected build therefore has not received a rendered retest. No alternate browser-control route was used to bypass that setting. Viewport overrides, keyboard-only completion, reduced-motion rendering, assistive-technology behavior and final screenshots cannot be certified from source review or DOM simulation alone.

## Release evidence

Final integration: **98 backend tests and 34 subtests; 33 local frontend tests; three separately run replay tests** passed. Ruff F/E9, diff whitespace checks, TypeScript and production build passed. The existing Starlette/httpx TestClient deprecation warning remains visible. Regression tests exercise quoted substrings/split lines, malformed records/envelopes, unknown pagination, mixed time zones, edit cautions, rejected-card export warnings and focus transitions.

A fresh v10 API smoke run completed live public GitHub import, one model evidence pair, save/reopen with prior note restoration, Markdown export and independent new-analysis decisions. Model runtime was **4.281 seconds**; source, analysis identity and checks are retained locally in `outputs/actual-api-smoke.json`. This is HTTP integration evidence, not rendered verification. A third agent re-reviewed the settled changes, including the final rejected-card export warning, and reported no further concrete blocker in the changed code. The parent inspected the diff and reproduced the combined checks.

## Remaining limits

This remains a human-review reading aid, not a code-fix verifier. Model semantics can still be wrong, and an additional agreement can still be extracted as a distinct ask. Markdown quotation handling is a bounded source-eligibility safeguard, not a complete semantic parser. No genuine contributor trial, independent human accuracy labels or measured human time savings have been obtained.

The Week 3 DEV entry remains unpublished. Final rendered verification, final article/link checks and the user's Week 3 eligibility/rights/rules confirmation remain separate publication gates.
