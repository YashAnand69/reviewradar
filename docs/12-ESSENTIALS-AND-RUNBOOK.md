# Essentials, ownership and operating guide

23 October 2026. Installation commands are verified in the release stage; this document separates prerequisites from measured results.

## Skills the build needs

| Area | Practical responsibility | Proof |
|---|---|---|
| Product and contributor workflow | Define the chore, exclude autonomous GitHub actions, distinguish request/response from code correctness | PRD, real discussion cases and a comprehension trial |
| Interaction and accessible UI | Paired evidence, source context, reversible local decisions, all error/empty states, responsive keyboard use | UI specification and browser acceptance runs |
| TypeScript/React | A single workbench with explicit local/replay adapters; no silent mode substitution | Type checks, component/domain tests and production build |
| Python/API/data design | Strict input and output schemas, immutable hashes, SQLite persistence, controlled exports | API, schema and restart regression tests |
| GitHub API | Public visibility/authorship checks, independent pagination and transparent limits | Mocked boundary tests and an actual dated import |
| Local inference | Pinned open weights/runtime, structured prompts, exact source validation, context budgets and bounded jobs | Actual model runs and negative-output tests |
| Evaluation | PR-level development/holdout split, request and pair scoring, separate engineering/human evidence | Dataset manifest, frozen predictions and error ledger |
| Security/privacy | Loopback-only processes, same-origin token bootstrap, safe text/links, no secrets in public files | Host/Origin/token matrix and release scan |
| Technical writing | Explain the specific chore and observed tradeoffs; credit human choices and AI work truthfully | Source-linked, sentence-level submission fact check |

No extra paid service, account integration, generative image library or model fine-tuning is required for the core product. Add a dependency only when it solves a demonstrated problem.

## Local infrastructure

The browser talks to a same-origin FastAPI app on `127.0.0.1:8893`. That app serves the built React frontend, stores snapshots/analyses/decisions in an ignored project-local SQLite directory and calls an authenticated local llama.cpp server on `127.0.0.1:18085`. The GitHub CLI is used only after an explicit import action. GitHub credentials remain in its existing authorization environment; the app's browser token is a separate per-process session token.

Internet access is needed to install dependencies/model weights and to import fresh public GitHub data. An already installed app can read saved snapshots and run inference without internet. Opening an original GitHub source link is an explicit external navigation. “Local-first” does not mean the initial downloads or live GitHub import work offline.

Public hosting contains a frozen replay and its source provenance. It has no visitor GitHub import, cloud model proxy, shared notes database or claim of fresh analysis. Replay interactions remain in that browser and can be reset; installing the local app enables the complete backend path.

## Prerequisites and cost boundary

- Python 3.12 and a supported Node release (the development build uses Node 24.19.0).
- The pinned llama.cpp build or a build of its pinned source revision.
- The pinned GGUF file: approximately 2.84 GB on disk. Other memory/runtime needs depend on hardware and configured context; do not promise the same latency on every laptop.
- GitHub CLI for live public import; a saved snapshot is an alternative.
- Free/local operation; no hosted API key, subscription, legal agreement acceptance or automatic purchase.

The model manifest records artifact size/checksum, revisions, runtime and tested context. `scripts/download_model.py` downloads only when explicitly invoked and verifies the exact artifact. `scripts/run_model.py` accepts explicit local runtime/model paths, checks provenance and refuses to take over an occupied port. A pre-existing application process must remain untouched.

## Data lifecycle and troubleshooting

Keep `.data`, `.runtime`, `.model`, `.venv`, dependencies and generated local outputs out of Git. Stop this application's server before removing its local data directory. This resets local snapshots, analyses and decisions; it does not delete downloaded exports, backups or public replay material, and is not a secure-erasure claim.

If GitHub import fails, retain the exact public URL and the safe error category; retry deliberately rather than repeatedly pinging an API. If the model is unavailable, source reading and an explicit chronology baseline remain usable. A baseline is not a model result. If a PR exceeds the token budget, select a smaller discussion or inspect its original sources; v1 does not secretly crop or chunk it.

If a result seems wrong, open full context, record a local note and report the source ID/analysis ID. A local reviewed decision organizes your session; it cannot repair a wrong model interpretation or change GitHub. Missing coverage and semantic errors belong in the evaluation ledger, even if the interface remains usable.

## Release handoff

Before publication, retain the source commit, dependency lock, model/run manifests, actual test output, public replay capture date, evidence error report, demo URL and draft. Recheck the Week 3 deadline and the article's factual claims. Final entry eligibility/rights/rules confirmation comes from the user immediately before publishing the single DEV entry. The previous challenge's acceptance is not reused.
