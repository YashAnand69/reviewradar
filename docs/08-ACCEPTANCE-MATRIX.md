# ReviewRadar: acceptance and evidence matrix

Initial plan, 23 October 2026. **All rows start unverified.** A requirement passes only with retained evidence for the actual release. This matrix is a release control, not a claim of perfection or a contest scoring prediction.

Severity: **Blocker** prevents publishing the affected claim/path; **Required** is necessary for the scoped complete app; **Enhancement** can be deferred explicitly. “Gate” describes expected behavior, not invented results.

| ID | Priority | Requirement and concrete acceptance | Evidence to retain |
| --- | --- | --- | --- |
| A01 | Blocker | New ReviewRadar project and repository created inside the Week 3 window; no repackaged Week 2 application | Initial commit, file history, original-source/third-party attribution |
| A02 | Blocker | A real local open-weight Gemma run performs the request/response task; model-less fallback is separately labelled | Bound input/output, model/runtime checksums/versions, run log and actual-app recording |
| A03 | Required | First-run public sample works without GitHub authentication and is plainly historical; local app can import a fresh valid public authored PR | Browser run and intake fixture/log with fetch timestamp |
| A04 | Required | User's stated scope is honored: selected public authored PRs, at most the documented cap, no private repositories or arbitrary URL fetching | URL/owner/public-visibility boundary tests and explicit form limits |
| A05 | Blocker | Comments, submitted reviews and inline threads are all represented; missing/pagination-capped/API-failed portions are named and invalidate a complete claim | Coverage counters, pagination tests, incomplete-input fixture and screenshot |
| A06 | Blocker | Exact original text and stable IDs survive ingestion; content hash changes on material snapshot change; repeated imports are deterministic | Hash/import regression checks and stored snapshot samples |
| A07 | Blocker | Untrusted model/source text cannot invent source links or commands, trigger a write, or inject executable rendered markup | Invalid-ID/quote/URL, prompt-injection, hostile Markdown/HTML and no-write checks |
| A08 | Required | Snapshot and analysis dates/identities remain bound across history, export and reload; no previous result is shown as freshly generated | Persistence/restart and stale-selection regression tests |
| A09 | Blocker | Every rendered request/response quote is an exact substring of its referenced comment in the same PR; proposed response is temporally later | Negative evidence-binding tests; manual semantic check of valid-but-wrong matches |
| A10 | Blocker | A response or “done” never becomes a verified code fix. Outdated/resolved GitHub thread state remains separate from interpretation and local review | Contradictory-state examples, component/API tests and wording review |
| A11 | Blocker | Oversized input, model timeout, invalid JSON, invalid evidence and unprocessed content cannot yield a clean completed empty queue | End-to-end error fixtures and coverage results |
| A12 | Required | Analysis and baseline declare `scope: human_review`; bot text remains in Sources with accurate actors, persistent exclusion scope and `comments_excluded_bots` counts. Neither queue implies automated-feedback coverage; approvals, thanks and author updates are not automatically actionable requests | Real and synthetic mixed-actor fixtures with labels/results |
| A13 | Required | Multiple distinct requests in one comment are supported or a documented coverage warning says they were not fully analyzed | Multi-clause example, expected card set and evaluation result |
| A14 | Required | New labels precede predictions; development and held-out examples are split by whole PR. Eventyay #6104, whose first failed output was inspected, is development-only; no tuning on holdout disguised as fresh evaluation | Label timestamps/commits, split manifest, complete result report |
| A15 | Required | Compare manual source reading and a serious deterministic review/thread/chronology baseline; report misses, false reminders, response-association errors, uncertainty and coverage | Evaluation command/script plus case-level outputs and denominators |
| A16 | Blocker | Small or failed evaluation is reported honestly. A raw-timeline copy does not rescue a missing request in the proposed queue; blanket abstention is not superior performance | Failure register, release notes and article claim audit |
| A17 | Enhancement | Genuine user trial measures total inspection/correction time and comprehension with balanced comparable tasks; disclose prior familiarity | Consented participant notes, protocol, actual timings and corrections; otherwise mark not conducted |
| A18 | Required | Within the initial screen a visitor understands the chore and can open a sample or import; the workflow is usable without a marketing scroll journey | First-time task run and screenshots at desktop/mobile widths |
| A19 | Required | Every card shows exact request, optional later response, source access, GitHub state, model interpretation and local disposition without conflating them | Contrasting-state screenshot and manual task check |
| A20 | Required | Loading, no requests, no comments, partial intake, unavailable model and malformed import are distinguishable and recoverable | Browser scenarios including keyboard focus/error announcements |
| A21 | Required | Local decisions persist and can be reversed; export includes source attribution, timestamps, uncertainty and incompleteness | Reload/undo/export tests and downloaded work-list inspection |
| A22 | Required | Keyboard focus, labels, headings and readable contrast work; 320px mobile has no blocked action or page-level overflow; motion respects reduced-motion | Browser/automated accessibility evidence plus manual keyboard/reduced-motion pass |
| A23 | Enhancement | Subtle motion communicates processing, evidence selection and saved decisions without masking latency, shaking layout or trapping focus | Ordinary/reduced-motion comparison; remove if distracting |
| A24 | Blocker | Backend and model stay on loopback; arbitrary Host/Origin, cross-site mutation and credential exposure are rejected according to the documented threat boundary | Security request matrix, config/log scan and actual bind verification |
| A25 | Blocker | GitHub credentials stay in the CLI/server environment and never enter browser payloads, SQLite, exports or committed output | Secret canary/boundary tests and release file scan |
| A26 | Required | Input/output sizes and times are bounded, response errors helpful, and only public canonical GitHub resources are fetched | Limit/timeout tests, SSRF-style URL rejection and API docs |
| A27 | Required | Local retention and deletion/reset procedure are documented; public replay contains only deliberately released minimal historical material | Privacy page, artifact manifest, verified reset and source notices |
| A28 | Required | Documented clean setup installs pinned dependencies, starts backend/frontend, loads sample and performs a model/baseline path; restart retains intended data | Setup transcript on named OS/runtime; limitations if not cross-platform checked |
| A29 | Required | Regression tests, type/build checks and independent full-diff audit pass for the release; exceptions are explicit | Test logs, reviewer findings, fixes and commit SHA |
| A30 | Blocker | Public replay says it is saved historical evidence; disabled/unavailable live operations do not pretend to work | Logged-out public browser verification and network review |
| A31 | Required | Public repository/demo/video links correspond to the current released behavior; no stale Week 2 assets or unsupported hosted inference claims | Release manifest and logged-out link check |
| A32 | Blocker | DEV draft uses required tags/template information, new-project/code/demo/open-AI/theme requirements and accurate partner category | Final article checklist mapped to official rules and release artifacts |
| A33 | Blocker | Article distinguishes human input, AI assistance, observed use, engineering checks and aspirations; every numerical claim has retained evidence | Sentence-level fact check, source links and verified screenshots |
| A34 | Blocker | Final user confirmation covers Week 3 eligibility, entry-material rights and rules; entry published once before deadline and public URL verified | Explicit confirmation, publication timestamp/URL and submitted commit |

## PRD traceability

Matrix IDs use the unique `A` prefix; PRD requirement IDs use `PRD01`–`PRD12` and remain separate. The following maps requirements to acceptance evidence, without claiming passage.

| PRD requirement | Matrix IDs |
| --- | --- |
| PRD01: first-run sample | A03, A18, A30 |
| PRD02: validated import | A04, A05, A06, A26 |
| PRD03: persistent incompleteness | A05, A11, A20 |
| PRD04: valid bound evidence | A07, A09, A10 |
| PRD05: distinct requests and non-requests | A12, A13, A14, A15 |
| PRD06: no automatic completion | A10, A19, A21 |
| PRD07: source context and chronology | A05, A12, A19 |
| PRD08: persistent reversible decisions | A08, A21, A28 |
| PRD09: honest export | A08, A11, A21 |
| PRD10: keyboard/mobile/reduced motion | A22, A23 |
| PRD11: recoverable model errors | A02, A11, A20 |
| PRD12: truthful public versus local | A03, A28, A30, A31 |

If PRD IDs change, update this map in the same integration change. Automated-source preservation is a source-view requirement, not a promise that the v1 model/baseline extracts bot requests.

## Model evaluation continuation target

The earlier research suggested a useful small-trial target: no labelled actionable request omitted from the proposed action/unclear view, materially fewer conversations requiring full inspection and approximately 30% lower total inspection effort in a genuine trial. These are **project targets**, not official judging requirements, proven results or population reliability guarantees. A tiny zero-miss sample cannot support “never misses feedback.” Lower effort cannot be inferred from latency or fewer UI rows alone.

If the model does not add useful extraction/association over the baseline, revise and retest development examples, expose limits and reduce claims. Never expand UI scope to hide a failed core task. If no genuine human trial occurs, A17 remains unverified and no human time-saving percentage may appear in the submission.

## Review dispositions

Use one status per row in the release ledger: `not started`, `implemented, unverified`, `passed (artifact)`, `failed (finding)`, `deferred (reason)` or `blocked (dependency)`. An enhancement may be deferred. A required feature needs a documented scope revision accepted in the plan before it is removed. A blocker cannot be waived by prose while the unsafe or misleading behavior remains publicly available.

Independent reviewers should inspect actual artifacts and name reproducible failures. “Looks good,” visual polish, a passing schema or a high self-awarded score is insufficient evidence for release.
