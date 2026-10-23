# ReviewRadar: execution stages and review gates

Planning baseline: 23 October 2026. These are planned artifacts and checks, not claims that they already exist. The decision contract in `00-DECISIONS-AND-CONTRACT.md` governs interfaces. Update that contract before parallel implementation changes an interface.

## Release outcome

A new local full-stack application that imports selected authored public PR discussions, proposes individual human-review requests and relevant later author responses, and lets a person inspect the evidence and keep local decisions. A judge can explore the same interface through an explicitly historical public replay and see actual local model processing in a recording. No automated changes to GitHub. No claim that a response proves a code fix. The v1 analysis and baseline deliberately use `scope: human_review`. All bot material remains in Sources, with persistent scope text and a count of excluded automated sources; the request queue does not claim to cover automated findings.

The full-stack release includes a working browser, backend, persistence, intake, model adapter, exports, tests, setup instructions and recoverable errors. It does not require cloud inference, private repository access, team accounts or an always-on hosted backend. These exclusions preserve the local-processing product promise rather than conceal missing endpoints.

## Execution ownership

The parent agent owns the contract, integration, repository, release and publication. Delegated agents own explicitly named files. Parallel work starts only after the shared interface is accepted; reviewers do not silently rewrite another agent's files. Each stage records its result, commands/checks, material findings, fixes and remaining limits in a release ledger. No stage is marked passed from a plan, screenshot alone or another agent's unverified claim.

## Stages

| Stage | Build and artifacts | Gate before proceeding | Response to failure |
| --- | --- | --- | --- |
| 0. Plan and challenge | PRD, TRD, UI essentials, evaluation/privacy plans, this schedule, acceptance matrix and submission strategy; independent document audit | Resolve conflicting states, coverage claims, scope, API contracts and model/data availability; every critical finding has an owner | Correct the documents before coding; defer features that obscure the core task |
| 1. Prove the difficult path | Fresh bounded public snapshots with provenance; initial labels made before model output; isolated local Gemma smoke test; deterministic baseline; request/response validation prototype | Actual local inference works on real discussion; exact source binding works; unknown/incomplete data stays visible; substantive request extraction or association adds useful evidence beyond statuses | Revise the prompt or explicitly narrow input scope and evaluate again on development data. Context chunking is deferred in v1; reject an oversized PR visibly rather than dropping text. If no advantage survives, keep the baseline usable and report the limitation; do not claim a successful AI task merely from valid JSON |
| 2. Implement local foundation | Backend schemas, SQLite migrations/initialization, snapshot hashing/import, public GitHub intake, history, model/baseline APIs, disposition and export | API regression checks cover wrong owner, bad URLs, partial pagination, malformed/oversize data, duplicate sources, missing model, invalid model evidence and persistence restart | Fix source/coverage/security errors before UI integration. Preserve failed input and readable error context without logging secrets |
| 3. Build the working interface | First-run sample, bounded intake, analysis progress, evidence workspace, filters, source timeline, local decisions, history/export; responsive and reduced-motion states | A first-time visitor can open a sample, inspect request plus response, understand historical/model/GitHub/local states and undo a local decision without instruction | Simplify labels and layout before adding motion; use direct task flows rather than a long promotional landing page |
| 4. Integrate and adversarially review | Real local browser flow; partial/error/empty cases; injection and hostile content fixtures; keyboard/320px-mobile pass; deterministic and model comparison report | Independent review of full diff plus test evidence; no release-blocking defects; public replay cannot masquerade as current live processing; no unsupported completion claim | Patch minimal confirmed defects; rerun affected checks and regression paths. Treat a missing actionable request as a model failure even when it remains in the raw timeline |
| 5. Verify usefulness | Small genuine user guide and optional author trial; inspect saved source evidence, correction burden, false reminders and missed requests against manual reading and baseline | Report actual denominators, labels, coverage and limits. Human trial requires actual participant actions; agent interaction is only engineering evidence | If no person is available, state that no human savings result exists. Do not invent a testimonial, ROI or proxy human timing. This does not prevent shipping an honestly evaluated prototype |
| 6. Package and release | Public source with license/notices, pinned dependencies, setup/run scripts, configuration example, release notes; frozen public replay, real local demo recording and verified URLs | Clean install/start check on documented environment; secrets/artifact scan; public links open without privileged login; model/runtime identities recorded | Repair setup or provide a precise documented environment limit. Remove stale/redundant assets. Never ship weights or claim public replay performs inference |
| 7. Draft and audit submission | Template-aligned DEV draft, concise screenshots, code/demo/evaluation links, meaningful Gemma category explanation, AI assistance and source credits | Every claim traced to a retained artifact; exact rules/tags/deadline rechecked; another agent reviews article and deployed experience; user can inspect the complete draft | Correct unsupported wording and broken links. Remove savings or superiority claims unsupported by actual checks |
| 8. Publish and verify | After the user's Week 3 eligibility/rights/rules confirmation, publish one DEV entry; record exact public URL/time and release commit | Published article visible, required tags and project links correct, category accurate, final source/demo matches article | Fix same-entry metadata/links rather than publishing a second competing entry; preserve a record of material corrections |

## Dependency order and parallelism

1. Stage 0 can divide product/UI, architecture/evaluation and delivery/rules research. Cross-review the other documents before freezing the initial contract.
2. Stage 1 comes before broad implementation. Parent owns model proof and real data. Eventyay #6104 has already been inspected in the first model proof, so the whole PR is development-only; its first poor model result is an identified failure requiring improvement, not a holdout or successful semantic proof. A second agent can independently label/adversarially review examples without seeing predictions. A third can prepare the interface shell against the agreed schema only after scope is accepted.
3. In Stages 2–3 backend and frontend may proceed in parallel, with a test/review agent on fixtures and critical failure cases. Do not let mocked frontend endpoints become a claimed working backend.
4. Stage 4 integration is sequential where a change depends on another fix. Independent accessibility and security reviews can run in parallel, but one parent adjudicates findings.
5. Stage 6 source packaging, demo preparation and draft writing can proceed in parallel once behavior and evaluation results are frozen. Final release checks and publication are sequential.

## Calendar and scope control

**23 October:** finish audited documentation, intake/model proof and first complete local flow. **24 October:** integrated workspace, adversarial checks, sample replay and user-guide availability. **25 October:** correct observed defects, release source/demo, audit article and publish after required confirmation. Aim to submit on 25 October IST, leaving contingency before the verified official deadline: **26 October 2026 at 12:29 p.m. IST**. The [official rules](https://dev.to/page/hacktoberfest-week3-2026-10-19-contest-rules) state 25 October at 11:59 p.m. PDT.

This calendar is an execution target, not a claim that timed tasks have happened. If delayed, preserve the core evidence workflow and cut enhancements in this order: custom graphics, optional shortcuts, snooze, extra filters, extra public samples, advanced history comparison. Never cut honest incompleteness, source validation, accessible essentials, actual inference verification or essential tests to fit the date.

## Review questions after every stage

- Does the deliverable work, or are we only looking at a convincing representation?
- What exact input was processed, and which material was skipped or not understood?
- Could the interface confuse a possible response with a verified fix, a historical state with current status, or an engineering test with a human trial?
- What failure would cost the user more effort than opening GitHub? Has it been exercised?
- Is new UI/features complexity justified by an observed problem?
- Can the next stage use the artifact without undocumented assumptions?

## Release stop conditions

Do not publish a release claiming a working model-assisted task while the model never ran, silently fails or provides no verified source evidence. Do not publish a judge-facing sample that fabricates current states, actions or people. Critical data leakage, model-triggered external writes, unsafe imported links, silent intake truncation and unreported missed labelled requests block their affected path until corrected. A clearly separated baseline or limited replay may remain available, with the AI limitation plainly disclosed; it must not be used to suggest the open-AI requirement has been met if the actual model path is absent.

Shipping a useful bounded project with documented limits is achievable. A flawless application or a contest win is not a testable delivery promise.
