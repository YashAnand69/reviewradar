# ReviewRadar

Find the request. Read the response. Decide what needs another look.

A new Hacktoberfest Week 3 project, begun **23 October 2026**. ReviewRadar reads selected public PR discussions and uses a local Gemma model to place individual human-reviewer requests beside possible later author responses. Exact evidence stays attached to its original source. It does **not** verify code fixes, resolve threads or write to GitHub.

## Project status

Planning and its independent audit are complete. The implementation is in progress. The documents describe acceptance targets; they do not certify that features or tests have passed. The release ledger will record actual checks and remaining limitations.

## Planning package

| Document | Purpose |
|---|---|
| [Contract](docs/00-DECISIONS-AND-CONTRACT.md) | Shared data/API boundary and deliberate exclusions |
| [PRD](docs/01-PRD.md) | Users, jobs, scope and acceptance criteria |
| [TRD](docs/02-TRD.md) | Architecture, intake, inference, persistence and failure handling |
| [UI essentials](docs/03-UI-ESSENTIALS.md) | Workbench, evidence hierarchy, responsive states and motion |
| [Evaluation](docs/04-EVALUATION-PLAN.md) | Baseline, labels, held-out cases and evidence limits |
| [Security and privacy](docs/05-SECURITY-PRIVACY.md) | Local trust boundaries, untrusted text and retention |
| [Implementation stages](docs/06-IMPLEMENTATION-STAGES.md) | Blank project through tested release and submission |
| [Submission strategy](docs/07-SUBMISSION-STRATEGY.md) | Rules, differentiation, demo and article gates |
| [Acceptance matrix](docs/08-ACCEPTANCE-MATRIX.md) | Concrete release checks and their evidence |
| [Trial guide](docs/09-TRIAL-GUIDE.md) | Genuine-contributor trial; no trial has yet occurred |
| [Planning audit](docs/10-PLANNING-AUDIT.md) | Independent findings, corrections and first model proof |
| [Execution ledger](docs/11-EXECUTION-LEDGER.md) | Actual stage results and unresolved work |

## Intended delivery

- React/TypeScript workbench, Python 3.12/FastAPI backend, local SQLite persistence.
- Read-only public GitHub intake through the existing `gh` CLI session; snapshot JSON import for offline use.
- Local Gemma inference through an authenticated, loopback-only llama.cpp server. No hosted inference or recurring API bill.
- Explicit **human-review focus**. Automated comments remain available and counted in Sources, rather than silently disappearing.
- Separate model interpretation, GitHub-reported state and your local reviewed/reopen decision.
- A public historical replay for trying the interface without installing a model; replay is not live inference.

## Limits that matter

A later author reply is not proof of a fixed defect or a satisfied maintainer. The model can miss or misinterpret requests. Every PR has its own coverage status; over-budget or failed analysis remains visibly incomplete. Private repositories, GitHub writes, automatic monitoring and code-diff verification are outside v1.

Actual setup, evaluation results and public links will be added only after verification. No selection probability, contest win, human-only authorship or human time savings is promised.

## Credits and licensing

Original application code: MIT. Gemma and llama.cpp are separately licensed upstream dependencies; weights/runtime binaries are not included. Public discussion excerpts retain their original authorship and are not relicensed by this repository. The source manifest and notices will identify any bundled historical material.

Yash selected the product direction and its real contribution-history problem. AI agents assisted research, planning, implementation and review. Engineering checks are distinguished from genuine human trials.
