# ReviewRadar

Find the request. Read the response. Decide what needs another look.

[Public historical preview](https://yashanand69.github.io/reviewradar/) · [Source](https://github.com/YashAnand69/reviewradar) · [Release checklist](docs/14-RELEASE-AND-SUBMISSION-CHECKLIST.md)

A new Hacktoberfest Week 3 project, begun **23 October 2026**. ReviewRadar reads selected public PR discussions and uses a local Gemma model to place individual human-reviewer requests beside possible later author responses. Exact evidence stays attached to its original source. It does **not** verify code fixes, resolve threads or write to GitHub.

## Project status

The complete local workflow is implemented and has passed API, persistence, adversarial and DOM integration checks. **This is a preview release, not a completed contest submission.** An initial rendered desktop/mobile pass and a real import-to-model browser flow exposed issues now covered by regression fixes. Browser access was disabled again before the corrected build could be visually retested; final keyboard/accessibility verification and genuine contributor validation remain incomplete. See the [follow-up audit](docs/15-FOLLOW-UP-AUDIT.md) for exact results and limits.

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
| [Essentials and runbook](docs/12-ESSENTIALS-AND-RUNBOOK.md) | Required skills, infrastructure, operation and handoff |

## Intended delivery

- React/TypeScript workbench, Python 3.12/FastAPI backend, local SQLite persistence.
- Read-only public GitHub intake through the existing `gh` CLI session; snapshot JSON import for offline use.
- Local Gemma inference through an authenticated, loopback-only llama.cpp server. No hosted inference or recurring API bill.
- Explicit **human-review focus**. Automated comments remain available and counted in Sources, rather than silently disappearing.
- Separate model interpretation, GitHub-reported state and your local reviewed/reopen decision.
- A public historical replay for trying the interface without installing a model; replay is not live inference.

## Limits that matter

A later author reply is not proof of a fixed defect or a satisfied maintainer. The model can miss or misinterpret requests. Every PR has its own coverage status; over-budget or failed analysis remains visibly incomplete. Private repositories, GitHub writes, automatic monitoring and code-diff verification are outside v1.

## Run locally

Requirements: Python 3.12, Node 24.15+ (tested 24.19.0), npm. GitHub CLI is optional for saved snapshots and required for live public import.

```sh
python3.12 scripts/setup.py
PYTHONPATH=backend .venv/bin/python -m reviewradar
```

Open `http://127.0.0.1:8893/`. Start with the historical sample, or import your own public PRs. The chronology baseline and source reading work without a model. `scripts/setup.py --node /absolute/path/to/node` supports an alternate Node installation. The app does not automatically read `.env` files; `.env.example` lists optional environment variables.

For real local inference, download the pinned model explicitly and build/provide the pinned llama.cpp runtime from `model-manifest.json`:

```sh
python3.12 scripts/download_model.py
python3.12 scripts/run_model.py --runtime /path/to/llama-server --model .model/gemma-4-E2B-it-Q4_0.gguf
```

Leave that model process running in a separate terminal. The launcher verifies the GGUF checksum and known binary checksum or reported pinned source commit, binds loopback, authenticates calls, disables context shifting and refuses an occupied port. The tested source-archive build reports its commit as unknown; its exact binary and source-archive checksums are recorded rather than misrepresented. Other platforms must build a runtime that reports the pinned revision. Full discussion processing remains local after the explicit GitHub import. Setup/model downloads require internet; saved evidence processing does not.

## Verify

```sh
.venv/bin/python -m pytest -q
.venv/bin/ruff check --select F,E9 backend scripts tests evaluation
cd frontend
npm test
npm run build
npm audit --audit-level=moderate
```

With the app running, `.venv/bin/python scripts/smoke_local.py --model --live-github` exercises an actual public import, inference, local decision/reopen and export. It does not write to GitHub. Omit both flags for a saved-sample/baseline check. These HTTP/DOM checks do not establish visual accessibility or genuine user savings.

The public replay is built separately with `python3.12 scripts/build_replay.py`; it does not replace the local frontend or contain a model proxy. Browser decisions there remain browser-local.

## Evaluation and remaining limits

The engineering pilot uses four PRs and seven pre-labelled requests, not a large benchmark or independent human ground truth. Development iterations and a frozen holdout are separated by whole PR. The untouched v8 holdout found the three labelled requests plus one repeated quotation as an extra request. A subsequent v9 quote-handling change is a **regression check**, not a fresh holdout; additional agreement can still be treated as a distinct ask. Do not treat these small counts as population accuracy. Source linkage and later-author constraints prevent invalid references, not semantic mistakes.

See [evaluation results](evaluation/REPORT.md) and [release audit](docs/13-INDEPENDENT-CODE-AUDIT.md). No contest win, selection probability, human-only authorship or human time savings is promised.

## Credits and licensing

Original application code: MIT. Gemma and llama.cpp are separately licensed upstream dependencies; weights/runtime binaries are not included. Public discussion excerpts retain their original authorship and are not relicensed by this repository. The source manifest and notices will identify any bundled historical material.

Yash selected the product direction and its real contribution-history problem. AI agents assisted research, planning, implementation and review. Engineering checks are distinguished from genuine human trials.
