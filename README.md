# ReviewRadar

Find the request. Read the response. Decide what needs another look.

[Public historical preview](https://yashanand69.github.io/reviewradar/) · [Source](https://github.com/YashAnand69/reviewradar) · [Release checklist](docs/14-RELEASE-AND-SUBMISSION-CHECKLIST.md)

A new Hacktoberfest Week 3 project, begun **23 October 2026**. ReviewRadar reads selected public PR discussions and uses a local Gemma model to place individual human-reviewer requests beside possible later author responses. Exact evidence stays attached to its original source. It does **not** verify code fixes, resolve threads or write to GitHub.

## Project status

The [Week 3 entry is published on DEV](https://dev.to/yashanand69/reviewradar-the-request-a-possible-reply-and-a-calmer-review-session-486). This remains an **experimental reading aid**, not a reliable task classifier. Current evaluation retains missed requests, duplicate suggestions and incorrect reply matches; see [evaluation](evaluation/REPORT.md).

Record **Not a request** or **Reply not relevant**, independently of notes and reviewed state. These decisions never rewrite model evidence or update GitHub. Select the original saved example or a mixed-evidence example preserving a real failure. A new panel exposes captured reviewer comments without a request card, including possible omissions; it does not certify complete coverage. Unsaved drafts survive card/example switches and reconnection in the open tab; save before closing/reloading.

No genuine contributor trial has occurred. The [feedback request](https://github.com/YashAnand69/reviewradar/issues/1) and [local-only trial guide](https://yashanand69.github.io/reviewradar/trial.html) are available. The new foreground launcher keeps the app/model in a dedicated Terminal; its actual ChatGPT-quit test remains outstanding. See [upgrade execution](docs/19-UPGRADE-EXECUTION.md).

## Use it for a returning review session

Open **Saved analyses**, search by account/repository/PR title, and load older readings when needed. Source capture dates remain distinct from analysis dates. **Check these PRs again** prefills the current selection for an explicit fresh import; the old reading and its notes remain unchanged. Choose the analysis mode after import.

When Gemma produces no cards, **Read reviewer comments without AI** creates a separate chronology reading list with notes, reviewed/reopen and export. It includes approvals and context, not just asks, and performs no request extraction or response matching. The original model result stays in history. See the [daily routine](docs/22-DAILY-ROUTINE.md) and [upgrade evidence](docs/21-DAILY-USE-UPGRADE.md).

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

## Keep the app running on this Mac

After setup, open **your own Terminal** and configure the model/runtime paths once:

```sh
.venv/bin/python scripts/local_services.py foreground --runtime /absolute/path/to/llama-server --model /absolute/path/to/gemma-4-E2B-it-Q4_0.gguf
```

For subsequent starts, **double-click `Start ReviewRadar.command` in Finder**. The launcher checks prerequisites, stops only this project's owned legacy launchd jobs, then runs a visible foreground supervisor in that Terminal. Keep the window open. **Ctrl+C stops this session's app/model children.** Do that before closing its window. There is no detached daemon, automatic restart or login-startup installation. Closing the chat app should not control an independently opened Terminal, but an actual user-start → chat-app quit → independent-browser check is still required before claiming this property verified.

The supervisor refuses occupied unmanaged ports and never takes over a process identified by a stale PID. It cleans up its own newly created process groups on startup failure, child exit or interruption. This includes the local model's descendant. Saved SQLite records remain. Save notes before closing/reloading a browser tab; unsaved drafts exist only in that tab. Do not start/stop during an import or inference.

`.venv/bin/python scripts/local_services.py status` distinguishes **legacy job ownership** from **endpoint health**. A healthy foreground session does not appear as a managed launchd job. `Stop ReviewRadar.command` stops only legacy jobs; use Ctrl+C in the foreground Terminal to stop the current session. Legacy `start` remains for compatibility, with its known ChatGPT-attribution limitation.

For a factual lifecycle check, run `.venv/bin/python scripts/probe_local.py --seconds 120` from a second independent Terminal, quit the chat app, and check `http://127.0.0.1:8893/` in Safari/Chrome while it stays closed. Record the actual quit time and browser result. The private probe records read-only endpoint health, not secrets or source contents; health samples alone do not certify that a quit occurred. See [reliability](docs/16-RELIABILITY-AND-PRACTICAL-USE.md).

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

The original four-PR pilot remains historical evidence. Fresh v10 testing exposed errors; v11 improved a specific response association but retained false tasks. v12 was rejected for losing genuine asks. The v13 test covered five of eight labelled actions. The v14 focused-comment revision recovered all eight on that exposed regression; a separate frozen six-PR test covered all six labelled actions with two duplicates. A broader set still produced 12 extra cards, and another exposed set retained five misses out of eight. Both v14 and v15 remain archived experiments and are not the shipped inference path. The retained v13 path also returned zero cards on a new live Eventyay #6104 check, failing the smoke test that expected its screenshot request. These adverse results remain in the reports. These are convenience samples, not independent human ground truth or population accuracy. Source validation prevents invalid references, not semantic mistakes.

See [evaluation results](evaluation/REPORT.md) and [release audit](docs/13-INDEPENDENT-CODE-AUDIT.md). No contest win, selection probability, human-only authorship or human time savings is promised.

## Credits and licensing

Original application code: MIT. Gemma and llama.cpp are separately licensed upstream dependencies; weights/runtime binaries are not included. Public discussion excerpts retain their original authorship and are not relicensed by this repository. The source manifest and notices will identify any bundled historical material.

Yash selected the product direction and its real contribution-history problem. AI agents assisted research, planning, implementation and review. Engineering checks are distinguished from genuine human trials.

## Follow-up daily workflow (after the contest cutoff)

The `improve/daily-use-followup` branch adds saved PR selections and exact capture differences. See [stage gates](docs/23-STAGED-PRACTICAL-UPGRADE.md). These changes are not part of the deadline submission.

Run `.venv/bin/python scripts/doctor.py` for offline setup diagnosis. Add `--verify-artifacts` to check the configured model/runtime hashes without executing them. Once dependencies are installed, double-click `Start Reading.command` on macOS to start source reading without downloading or starting a model. It leaves existing services untouched and fails if the port is occupied. Keep the Terminal open. The full model launcher remains separate.

The [comparative trial protocol](docs/24-COMPARATIVE-TRIAL.md) measures reading, correction and setup effort against direct source reading. No completed participant comparison is claimed.
