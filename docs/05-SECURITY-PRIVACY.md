# ReviewRadar security and privacy requirements

Planning threat review · 23 October 2026. This is a bounded local tool, not a multi-user hosted service or a security certification.

## Assets, trust and limits

Protect the local GitHub CLI session, fetched source discussions, local decisions and notes, model configuration and database integrity. The first release accepts public authored PRs only and analyzes an explicitly labeled human-review queue. Bots remain in the original Sources view and are counted as excluded from analysis; completeness applies to that declared scope, not every possible review obligation. Public source material can still include personal information; local storage and exports deserve deliberate handling. The threat model includes hostile imported JSON, malicious review text, a malicious website attempting to reach localhost, and a compromised or unexpected model response. It does not protect against malware or another user with equivalent access to the local account.

Model output and GitHub bodies are **data, never authority**. No comments, requests, credentials, system prompts, local files or arbitrary network tools are exposed to the model beyond the selected bounded snapshot. The model cannot comment, push, resolve threads, change review state or run commands. Do not claim prompt injection is solved merely because the prompt asks it to ignore instructions; constrained capabilities and output checks are the actual boundary.

## Local network boundary

- Bind the app and model to `127.0.0.1`, not `0.0.0.0`. Use project-owned ports and do not stop another application's process. Reject external model endpoints in normal local mode; never silently route to a cloud provider.
- Allow only configured loopback hosts. Validate the Host header against the exact release host/port expectations to reduce DNS-rebinding exposure. Do not accept proxy-forwarded host headers or arbitrary `localhost.evil.example` suffixes.
- Serve release UI and API from the same origin. Do not enable wildcard CORS. Reject cross-origin browser API requests; all mutation requests require the exact configured Origin, JSON content type and a per-process unpredictable app session token. Refuse absent/malformed Origin for writes, including localhost command-line callers unless they explicitly supply it.
- Bootstrap only the app session token through same-origin runtime configuration. It is not a GitHub credential. Serve it `no-store`; do not put it in a URL, log, persistent browser storage or public static replay. Other websites must not be able to read it via CORS. A local process or the user can still access it; this is not user authentication.
- Require the app token on data-reading APIs too. Keep the health response non-sensitive. Apply host/origin handling to errors as well as successful routes. Content Security Policy, `nosniff`, no framing and a restrictive referrer policy are defense in depth, tested against the built UI.

The token does not make an exposed public server safe. Public mode is static replay with no visitor import, no model proxy and no local credentials. Do not publish the FastAPI port through an unauthenticated tunnel.

## Intake and credential boundary

Use the installed GitHub CLI's existing authorization for read-only API calls. Do not read or print its credential store. Browser inputs choose canonical public PR URLs and a login, never an executable, API endpoint, GraphQL query or shell fragment. Use subprocess argument arrays with timeouts and bounded output. Confirm repository visibility and PR author before storing. Github.com-only URLs, public checks and rejection of redirects prevent an arbitrary fetch proxy. API responses may be partial or stale; preserve warnings.

Strict schemas bound JSON bytes, PR/comment counts, text lengths, timestamps and duplicate source IDs before persistence or inference. Recompute snapshot IDs. Imported provenance is user supplied and should be labeled **imported**, not GitHub verified, even if its source field claims GitHub. Validate source URLs structurally against the PR namespace and allowed GitHub anchor forms. Exact quote validation establishes correspondence to imported evidence, not authenticity of the imported evidence.

No credentials, browser cookies, environment dumps, private content, model weights or runtime archives belong in Git. Ignore local data directories; scan tracked files before release. Error responses and logs use safe categories and record IDs, not full source bodies, tokens or subprocess stderr. Package installation is explicit and pinned; the app does not auto-install dependencies or execute a downloaded model-suggested command.

## Rendering and export

Render source bodies, model rationale and user notes as escaped text. Avoid raw HTML and Markdown rendering in v1. External source links come only from validated snapshot URLs, open with `noopener noreferrer`, and are visibly marked as GitHub. Do not create clickable model-supplied arbitrary links. A malicious review containing a URL remains inert text.

Export is an explicit local download. Safely delimit and escape content so a source quote cannot impersonate an export section or inject an active link. Include completeness, source date, model mode and uncertainty. Warn that downloaded exports are not deleted when the local database is cleared. Static public samples contain only reviewed public excerpts and minimal necessary author information; identify original sources and state that authors' comments are not relicensed by the software's license.

## Data lifecycle

Store the SQLite database in an ignored project-local directory with restrictive permissions where supported. Use parameterized queries and atomic writes; never interpolate model text into SQL. Snapshot and analysis records are immutable; user decisions are separate rows. Do not send telemetry, analytics, crash payloads or discussion bodies to a hosted service. Network access is limited to explicit GitHub import, dependency/model installation when the operator chooses, and user-opened original source pages.

Document exactly where data lives and how to stop the app and remove local data. If a Delete action is implemented, delete dependent dispositions/analyses transactionally and refresh the interface. Do not promise secure erasure from disk, backups, browser downloads or already published public sample files. A refresh makes a new snapshot; it does not silently overwrite a previous audit trail.

## Mandatory adversarial checks

| Test | Expected result |
|---|---|
| Foreign Host / spoofed forwarded Host | Request refused |
| Foreign or missing Origin on mutation | Request refused, no data changed |
| Missing/incorrect app token on data API | Request refused |
| Cross-origin read of runtime config | No readable token through CORS |
| Non-GitHub URL, userinfo, port, unexpected path | Import rejected before network request |
| Private repository accessible to CLI | Import rejected |
| Shell syntax in login/URL | Validation failure; never executed |
| Imported HTML, script, Markdown links | Displayed inertly as text |
| Fake quote/source ID, different PR response | Analysis visibly fails; no misleading success |
| Review text requesting system data or command execution | No tool or secret access; output still validated |
| Model timeout, token overflow, invalid/truncated JSON | Visible incomplete/error state, no clean queue |
| Cap reached / nested pagination remains | Snapshot explicitly incomplete |

Keep the result of each check in the release audit. These controls must be implemented and tested before the submission says they exist.

## Primary references checked

[Starlette middleware](https://starlette.dev/middleware/) documents host and CORS facilities; using a framework alone does not enforce this project's intended policy. [FastAPI middleware](https://fastapi.tiangolo.com/tutorial/middleware/) describes request/response interception, which can implement and test the local boundary. [GitHub's API limits](https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api) inform bounded read-only import behavior. [The pinned llama.cpp server](https://github.com/ggml-org/llama.cpp/blob/98801578818b26d833a1fe244870d64b0c34bb46/tools/server/README.md) is a separate local service and should receive the same least-exposure treatment.
