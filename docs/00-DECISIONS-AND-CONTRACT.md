# ReviewRadar: architecture contract
Status: planning draft revised by early independent audit, 23 October 2026. Read before delegated design. No implementation until planning audit is integrated.

## Selected delivery
A new local full-stack application: React + TypeScript + Vite interface, Python 3.12 FastAPI backend, SQLite persistence, loopback-only app/model. Public static sample uses the same interface and immutable saved evidence, explicitly replay mode. GitHub import supports public PR URLs through read-only gh CLI/API calls; no credential in browser. Snapshot JSON import enables offline use of already-fetched data. No private repo support in first release. Parent verifies model on an isolated port using existing pinned open Gemma weights/runtime, without interrupting other apps. No paid service or cloud inference.

## Stable wire types (v1)
Snapshot: {schema_version:1, id:contentSHA256, fetched_at:ISO, source:"github"|"import"|"synthetic", owner:string, prs: PR[], complete:bool, warnings:string[]}.
PR: {id:"owner/repo#number", url:httpsGitHubPull, title:string, author:string, state:"OPEN"|"CLOSED"|"MERGED", head_sha:string|null, fetched_at:ISO, complete:bool, warnings:string[], comments:Comment[]}.
Comment: {id:stableSourceID, url:validatedGitHubCommentURL, author:string, is_bot:bool, kind:"comment"|"review"|"inline", body:string, created_at:ISO, updated_at:ISO, review_state:string|null, thread_id:string|null, thread_resolved:bool|null, thread_outdated:bool|null}. Original text retained exactly. Comments sorted timestamp then sourceID. All source URLs same GitHub PR namespace. No model links permitted. Enforce PR author matches supplied owner case-insensitively. PR author responses must be strictly later than the request and in the same PR; equal timestamps do not establish a response. Full original source text is visible, not just a quote.
Analysis: {id:string, snapshot_id:string, mode:"model"|"baseline", scope:"human_review", model:string|null, prompt_version:string, created_at:ISO, complete:bool, warnings:string[], cards:Card[], coverage:Coverage[], stats:{comments_total:int, comments_processed:int, comments_excluded_bots:int, elapsed_seconds:number}}.
Coverage: {pr_id:string,status:"analyzed"|"failed"|"rejected_oversize",comments_total:int,comments_processed:int,comments_excluded_bots:int,reason:string|null}. Per-PR failure remains visible even when zero cards. Configured context is 16,384 tokens on the verified local server; reserve 2,048 output tokens plus at least 1,024 safety tokens (configuration must match actual runtime). Tokenize complete PR context with runtime before inference and reject over budget instead of truncating. A PR with any invalid output cannot be counted fully analyzed. The snapshot preserves all comments. Model/baseline queue scope is human reviewer comments with human author responses; bot comments remain in Sources with explicit excluded-bot counts. Processed counts refer to non-bot comment inputs. Completeness refers to this labelled scope, not all automated feedback. Known bots and PR-author updates cannot be emitted as reviewer requests. Failure preserves the snapshot and successful PR results.
Card: {id:string, pr_id:string, request:{comment_id:string, quote:string}, response:{comment_id:string, quote:string}|null, category:"change"|"question"|"suggestion"|"unclear", interpretation:"follow_up"|"possibly_responded"|"unclear", rationale:string, uncertainty:string[], github:{review_state:string|null,thread_resolved:bool|null,thread_outdated:bool|null}}.
Disposition stored separately: {analysis_id:string,card_id:string,state:"open"|"reviewed",note:string,updated_at:ISO}; all model cards initially open. User action never changes GitHub or snapshot. New analysis new dispositions, no automatic completion.

## API
GET /api/health => {status:"ok",version,model_configured:bool,github_available:bool,mode:"local"}.
GET /api/snapshots => summaries.
GET /api/snapshots/{id} => Snapshot.
POST /api/snapshots/import {snapshot:SnapshotWithoutRequiredID} => validated Snapshot (recomputeID).
POST /api/snapshots/github {urls:string[],owner:string} => Snapshot. Max 5 PRs initially, public only, fetch bounded 60s, pagination cap visible; no silent drop.
POST /api/analyses {snapshot_id,mode:"model"|"baseline"} => Analysis; synchronous bounded per PR calls, max input bounded, reject oversized instead of silently cropping. UI shows honest elapsed state. Max selected sample 5 PRs.
GET /api/analyses => summaries; GET /api/analyses/{id} => Analysis; GET /api/analyses/{id}/export => Markdown.
PUT /api/analyses/{id}/cards/{card_id}/disposition {state:"open"|"reviewed",note} => Disposition; GET /api/analyses/{id}/dispositions => Disposition[].
GET /api/sample => bundled curated public snapshot (provenance; historical), if available.
JSON errors {detail:string}. Bounds defined centrally. All app writes require exact allowed Origin; API token required on non-health routes with browser bootstrapping through same-origin runtimeconfig. No CORS *. No GitHub token sent to browser.

## Deliberate deferrals
Snooze, automatic background refresh, private repositories, GitHub writes, per-diff code verification, cross-PR duplicate detection and context chunking are excluded from first release. Integration must use this contract or update it before parallel implementation. No one claims above API exists yet.
