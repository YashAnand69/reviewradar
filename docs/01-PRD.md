# ReviewRadar — product requirements

Version 1 · 23 October 2026 · Planning specification; outcomes below are targets, not achieved claims.

## 1. Product decision

**ReviewRadar places a specific review request beside a possible later response, so an open-source contributor can decide what deserves another look without rereading every conversation.** It is a conversation-reading aid, not a code reviewer, repair agent, merge-readiness assessor or authoritative list of unresolved obligations.

Build a new local-first full-stack application. Users explicitly select up to five public PRs they authored. The server reads public GitHub conversation data or a validated exported snapshot, and a local open model proposes request-level evidence cards. Every quote is checked against an immutable source snapshot. The user opens the original context, records a local decision, and exports a source-linked review sheet. No GitHub mutation is available.

The public demo is the same workbench running a clearly labelled, dated replay. It does not pretend to import a visitor's GitHub history or run a local model in their browser. The downloadable/local application provides live import and actual inference.

## 2. Problem, evidence and limitations

An authored PR can contain an inline request, a separate question in a review summary, an author's later explanation, bot notices and a later approval. PR-level statuses compress this detail. Conversely, an old `CHANGES_REQUESTED` review can create a false reminder after the contributor has responded. Finding the relevant passages across several discussions is the narrow chore being tested.

Prior research found real historical request/reply examples in Eventyay #6104, Visdom #1864 and #1872, and VoxBento #718. Those establish accessible test material; they do not establish current outstanding work, actual model quality or time savings. A bounded sample of five open PRs had no substantive human review, so this product must handle low-demand and empty states honestly.

Graphite PR Inbox and GitLens Launchpad already organize PR follow-up. GitHub and Copilot already support review reading. The proposed distinction is **individual request-to-response evidence across selected authored PRs**, tested against original-source reading and a serious deterministic chronology/status baseline. Local processing and citations alone are not novel. See the dated research report under the parent project's `outputs/HACKTOBERFEST-WEEK3-RESEARCH/AUDIT-AND-FINAL-PROPOSITIONS-OCT22.md`.

## 3. Users and jobs

| User | Job | Successful outcome |
| --- | --- | --- |
| Contributor with several authored PRs | Resume a review session after a gap | Find a specific request, read its possible response and decide what to inspect next |
| Contributor finishing a response | Check whether their explanation addresses the original ask | Compare passages and retain a local note; no claim that the implementation is correct |
| Contributor revisiting an old PR | Understand apparently stale review status | See actual approval/thread state and dated conversational evidence without treating either as proof |
| Judge or first-time visitor | Understand the workflow before installing anything | Explore a real, attributed historical sample immediately, then see exactly how to run the local engine |

One primary contributor and one session at a time. No organization administrator, maintainer analytics or team assignment features in v1.

## 4. Core workflow

1. **Choose a source.** Open the supplied historical sample, import a snapshot JSON, or enter a GitHub handle and one to five public authored PR URLs in the local app. Explain privacy and source scope before import.
2. **Inspect coverage.** Show PR titles/states, fetch time, comment/review/inline counts, and explicit missing/capped/failed coverage. Validate the author against the handle. Reject private or off-GitHub URLs. Import is read-only.
3. **Choose analysis.** Offer “Local model” only when configured, and a clearly named “Chronology baseline” alternative. Show the selected snapshot and local model identity. A failure never silently switches to baseline. A dated saved replay is not presented as fresh inference.
4. **Review evidence.** Show separate request clauses, possible later responses, category, uncertainty and independently reported GitHub state. Default view includes all model interpretations, including possibly responded and unclear. The request queue focuses on human review. A persistent scope label and excluded-bot count link to Sources, where every automated comment remains visible and labelled; analysis completeness applies only to the stated human-review scope.
5. **Make a local decision.** Mark a card “Reviewed locally” or reopen it. Optional note records the user's reasoning. This action never resolves a thread, comments on a PR or certifies a fix. Reviewed items remain accessible through a visible filter and count.
6. **Export or return to GitHub.** Export a Markdown review sheet with source URLs, snapshot date, model/baseline identity, limitations and local decisions. Original GitHub links open independently. Reimporting creates a new snapshot/analysis and does not silently apply stale decisions.

## 5. Scope and priorities

### Must ship

- Public GitHub intake covers general comments, submitted reviews and inline conversations, with deterministic source identity and dates.
- Full pagination within documented resource limits; limit/error conditions are shown as incomplete, not as a clean result.
- Offline snapshot import with schema, size, URL namespace and author validation. Imported display text is untrusted.
- Immutable snapshot binding for every analysis and source quote; timestamp-ordered events retained for context.
- Local model extracts distinct requests and associates only later, relevant responses from the same PR. Exact quote validation is necessary but not sufficient: evaluation checks semantic relevance too.
- All cases preserve three separate concepts: model interpretation, GitHub-reported state and user disposition.
- No human request is silently hidden because it is optional, outdated, in a closed/merged PR, or classified as possibly responded. Bot comments are explicitly excluded from the human-review queue and preserved in Sources with a visible excluded count.
- Side-by-side request/response evidence with original comment context and accessible GitHub links.
- Readable review queue with PR/category/interpretation filters, visible totals, local reviewed/reopen state, and note persistence.
- Export and clear local-data deletion/reset instructions. Public replay has explicit local-only temporary interaction semantics.
- Model availability, processing, failure and partial-coverage states; honest elapsed time, not invented percentage progress.
- Public sample usable without sign-in, keyboard support and mobile reading, and reduced-motion support.
- Setup guide, source, dependency/model provenance, regression tests, bounded evaluation and submission materials.

### Should ship if core gates pass

- A compact timeline of the selected PR's comments and review submissions.
- A direct full-source-reading mode and deterministic baseline comparison.
- A short reproducible real-inference recording tied to a specific fixture and model artifact.
- A five-minute genuine-contributor trial guide with consent, corrections and total effort measurement.

### Explicitly defer

Snooze, scheduled sync, notifications, GitHub OAuth, private repositories, organizations/teams, background monitoring, code-diff analysis, fix verification, generated replies, PR editing, CI repair, automatic thread resolution and GSoC predictions. No secondary landing-page product, chat interface, 3D scene or decorative partner integration.

## 6. Interpretation and copy rules

| Concept | Allowed label | Forbidden implication |
| --- | --- | --- |
| Extracted ask with no associated response | “Follow-up to inspect” | “You must fix this” or a proven outstanding obligation |
| Later passage appears relevant | “Possible response found” | “Fixed”, “complete”, “maintainer satisfied” |
| Ambiguous request or association | “Needs interpretation” | Confidence theatre or silently discarded card |
| GitHub resolved/outdated flag | “GitHub thread: resolved/outdated” | Verification that code is correct |
| Local user action | “Reviewed locally” | GitHub state changed |
| Zero model cards | “No requests identified in this analysis” | “All caught up” or “nothing needs attention” |
| Import/model limitation | “Incomplete — inspect source” | A quiet empty queue |
| Historical public demo | “Replay · captured [date]” | Live inbox, live analysis or current task status |

Avoid a single risk score, overall completion ring or merge-readiness percentage. Rationale is concise and tentative; original evidence is visually stronger than generated explanation. Preserve required AI-assistance disclosures in project and submission copy.

## 7. Acceptance criteria

| ID | Requirement and pass condition |
| --- | --- |
| PRD01 | A fresh visitor opens the sample and reaches a specific source-linked evidence pair without account setup. Replay date and mode remain visible. |
| PRD02 | Importing a valid public authored PR snapshot retains exact comment text and dates; wrong author, unsafe URL, malformed file and oversized input produce actionable errors. |
| PRD03 | A partial GitHub fetch or analysis displays persistent incompleteness, which remains visible after filtering and when there are zero cards. |
| PRD04 | Every displayed model quote matches its referenced source text, its card belongs to that PR, and a response is later than the request. Invalid model evidence is rejected visibly rather than rendered as valid. |
| PRD05 | Multiple requests in one comment can appear separately; an approval, praise-only comment and author update are not automatically actionable requests. Evaluation checks these behaviours using labelled examples. |
| PRD06 | Possible responses, resolved threads and later approvals do not automatically hide or mark cards reviewed. |
| PRD07 | The user can inspect full comment context and source chronology, distinguish actor/bot labels, and reach validated GitHub evidence in one action from a selected card. |
| PRD08 | Mark reviewed, add note, reload and reopen work locally without any GitHub write. A new analysis starts with independent dispositions. |
| PRD09 | Export includes snapshot date/completeness, mode/model, evidence URLs, uncertainty and local decisions. Empty/failed analysis cannot export a misleading clean bill. |
| PRD10 | Keyboard-only operation reaches all actions; visible focus, labelled controls, meaningful headings and reduced motion work. At 320 px width evidence remains readable without page-level horizontal scrolling. |
| PRD11 | Model unavailable, timeout and invalid output show useful next steps and preserve the snapshot. Switching to baseline requires explicit user selection. |
| PRD12 | README and public demo explain which capabilities need local installation. No public UI button claims an unavailable server action succeeded. |

The independent acceptance matrix and test evidence should cite these IDs; a checkbox is not proof without the corresponding recorded check.

## 8. Validation and continuation gates

Use about 20–30 real conversation examples only if the available public history supports that many. Document fewer examples honestly. Label requests/response links before model inspection; split whole PRs between development and holdout so different cutoffs of one conversation cannot leak. Agent/parent labels are engineering labels, not customer validation.

Measure missed requests, false reminders, incorrect associations, invalid citations, abstention and how many conversations still require original-source inspection. Include ambiguous human findings, and separately evaluate visible bot exclusion and complete source preservation. An exact valid quote attached to the wrong request is a failed association. A raw timeline does not rescue a missed item from the proposed queue.

A genuine human session compares total reading/correction effort against original GitHub reading or matched source views. The prior proposed 30% improvement is an aspiration, not a release claim or statistical finding. Record familiarity with the user's own PRs. Do not represent agent-operated timing as a human trial. If the model provides no demonstrated benefit over baseline, ship the result honestly or narrow the claim rather than using interface polish to conceal failure.

## 9. Risks and unresolved assumptions

- **Demand:** current volume of substantive feedback is not established. Historical examples can test mechanics without establishing daily usefulness.
- **Semantic safety:** the small local model may miss distinct requests, associate generic “done” incorrectly or over-abstain. Strict validation cannot repair semantic error; holdout evaluation is a release gate.
- **Context limits:** long conversations can exceed model context. The technical design must reject visibly or use a documented, evaluated chunk strategy; never silently truncate.
- **GitHub limits:** permissions, API limits, deleted/edited comments, pagination and review-thread availability can reduce coverage. Snapshots are dated evidence, not current truth.
- **Privacy:** public comments can still contain personal data. Keep the curated fixture minimal and attributed, provide local deletion instructions, and never bundle credentials.
- **Adoption:** installing a local model is substantial friction. The replay demonstrates value first, but is not a substitute for a working local engine.
- **Contest:** deadline, eligibility and judging remain external rules; verify them near submission. Winning cannot be guaranteed, and genuine user evidence is not yet available.

## 10. Release definition

A complete v1 is a functioning local import → analysis → evidence inspection → local decision → export path; a truthful public replay; reproducible setup and checks; evaluated model behaviour with limitations; and a submission draft whose claims match evidence. Publication follows final rules/rights confirmation. Neither a polished mockup nor a queued submission is a finished release.
