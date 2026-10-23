# Stage-zero independent planning audit

23 October 2026. Parent integration of three design agents and cross-reviews. This is a planning audit, not a release certification.

## Findings and changes

| Priority | Finding | Resolution |
|---|---|---|
| P1 | Global completeness cannot identify a failed PR. | Add coverage item for every PR, with processed/excluded counts, explicit failure and preserved sources. Never call a failed zero-card result clean. |
| P1 | Context budget conflicted between 8,192 and 16,384. | Isolated pinned server was started on an unused loopback port and reported 16,384 context. Reserve 2,048 generation plus 1,024 safety tokens; tokenize actual template; reject overflow, no untested chunking. |
| P1 | Bot inclusion promises contradicted model scope and would bury useful human asks in generated guides. | v1 explicitly focuses on human review. Preserve all bots in Sources, expose their count and scope persistently; no claim to cover all automated feedback. |
| P1 | Baseline comments called requests would imply nonexistent semantic analysis. | Baseline label is Comments to inspect. Never automatically substitute baseline for failed model. |
| P1 | PRD and acceptance IDs overlapped with different meanings. | PRD uses PRD-prefixed IDs; delivery matrix identifiers are distinct with traceability. |
| P1 | Exact citations alone cannot validate semantic relevance. | Evaluate request recall/precision and response relationships separately; wrong-but-exact quotes remain errors. |
| P1 | Initial whole-PR development inference emitted author updates, praise and empty approval. | Hard-veto PR-author/bot/empty requests; separate reviewer sources from response candidates; add contrast examples. Second development probe found the screenshots request and its later author reply. Both probes retained; neither is held-out evidence or customer validation. |
| P2 | Source quote without surrounding context invites false certainty. | Full original comments and chronology remain readable beside evidence. |
| P2 | Mobile width gate differed; stage plan suggested deferred chunking. | Adopt 320px and whole-PR rejection consistently. |
| P2 | Token bootstrap could depend on the token it delivers. | Runtime config is same-origin no-store bootstrap, without API-token prerequisite. Data APIs require token; writes also require exact Origin. Host allowlist and no CORS prevent casual cross-site reads. Not user authentication. |
| P2 | Snooze/background sync add state complexity before proof. | Defer. Reviewed/reopen and notes provide the complete first workflow. |

## Proof performed before broad implementation

Existing verified Gemma 4 E2B Q4_0 weights and pinned llama.cpp build were used through a new authenticated process; no previous application source was copied or process stopped. Runtime health and model identity succeeded. Eventyay #6104 was explicitly development material. First prompt: 10.31 seconds, wrong semantic output. Revised structured/few-shot prompt: 8.07 seconds, one genuine reviewer ask linked to the relevant later author screenshot report. No independent human label, accuracy or time-saving claim follows from this single example.

## Decision

Proceed with the bounded full-stack build after these document corrections. Core interpretation remains a pilot requiring independent labelled cases and adversarial checks before release. Stage-one proof is sufficient to begin engineering, not to claim a winning or reliable finished product. Remaining gates: real intake coverage, strict validation, model errors/limits, useful UI, persistence, evaluation, independent code review, clean installation, public provenance, recording and final submission fact check.
