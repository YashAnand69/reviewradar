# v17 isolated-comment experiment — not promoted

The frozen 20-case exposed regression completed on 26 October 2026 from 07:04:02 to 07:05:38 UTC, after the Week 3 submission cutoff. All inputs and candidate identity are in candidate.json; preserved per-case outputs and timing are under ignored outputs/upgrade/v17-candidate/first-run. The active model remains v13.

The candidate recovered the options-mutation request in Visdom #1954, the branch-update request in #1919 and the PR-template request in #1928. It also emitted harmful false tasks: bot invocations in Visdom #1952 and Open Prices Frontend #2472, and three completed-action statements in JSON Schema Test Suite #1234. The branch-update request was paired with generic test results rather than evidence that the branch was updated. Rationale duplicates remained in #1954 and #1919.

These directly observed counterexamples are sufficient to reject default promotion; this report does not claim a completed independent aggregate semantic score. The implementing agent hit its usage limit after the run. The parent inspected preserved predictions and did not tune, rerun or relabel them. Independent semantic review remains pending. Recovering more asks does not justify introducing false tasks or weak response associations.

No new runtime, model purchase, active model-file edit or application database mutation occurred in this experiment. The original protocol requires independent review before promotion. No fresh benchmark, general accuracy percentage, real-user time savings or contest improvement follows from this exposed regression.
