# Reliability and practical use — 24 October 2026

## Why the page said “action did not finish”

At the start of this audit, neither the app on port 8893 nor the model on port 18085 was listening. The browser retained an older interface, whose network request failed. Earlier successful tests established behavior while the services were running, but did not establish that terminal-bound processes would remain alive after the chat ended. The previous message overstated practical readiness by not separating those two facts clearly enough.

A second recoverability problem was the rotating local session token: after a backend restart, a tab could hold the old token. A third was model configuration being inferred from a credential file alone, despite an unavailable model server.

## Implemented corrections

- macOS project-specific login-session services, with private ignored configuration/logs, restart after a crash and no dependency on the chat terminal. Nothing is installed as a login-startup item. Start again after logout/reboot.
- Explicit start/status/stop commands, ownership checks and rollback of only newly started jobs. Existing model checksum verification remains mandatory. Unrelated processes are not stopped or replaced.
- Actual authenticated model readiness checks validate model identity and context without generating text. A missing/stopped model does not prevent baseline source reading.
- Session renewal occurs once after an authentication rejection, before an action could execute. Network failures do not automatically repeat a potentially completed write or inference call.
- Connection errors preserve loaded evidence and unsaved notes in the open tab. Reconnect remains available after dismissing an alert. A successful recovery clears only the relevant connection error.
- Returning to the tab checks availability; there is no continuous background polling. Offline views link explicitly to the historical public replay rather than silently pretending to switch to live inference.

## Practical contributor workflow

Use ReviewRadar when returning to a few PR conversations after an interruption. Import up to five selected public PRs you authored, inspect source completeness, then choose Gemma extraction or the deterministic chronology baseline.

In the Eventyay historical example, a reviewer requests screenshots and the author later reports adding them. Gemma proposes that connection. A useful next action is to inspect the actual attachments against the requested behavior, record what still needs checking, and export the source-linked note. “Reviewed locally” means you completed your own reading; it does not mean the maintainer approved the change or the code is correct. All replay cards are historical, possibly-responded examples, not a current unanswered inbox.

The baseline orders human comments. Gemma proposes individual requests and their semantic relationship to a later reply. That can reduce searching, but we have not measured net human reading/correction savings. Source access and reversible notes support the real decision rather than replacing it.

## Lessons applied from actual winning work

The [official Week 1 winner announcement](https://dev.to/devteam/congrats-to-the-hacktoberfest-open-source-ai-challenge-touch-grass-winners-152c) names Paper Trail as overall winner and Grow a Song for Gemma. [Paper Trail](https://dev.to/mikek/paper-trail-gemma-writes-your-walk-a-field-card-then-the-screen-goes-away-3mf4) provides a finished example and explains setup, failures and residual errors. [Grow a Song](https://dev.to/anshsaini/grow-a-song-my-run-wrote-its-own-soundtrack-with-gemma-running-on-my-phone-44ml) supplies an actual session artifact and explains a crash correction. These are observed practices, not access to the judges’ private reasoning.

ReviewRadar now emphasizes a short real task, explicit setup/recovery, source-bound output and an honest failure account. The [Week 3 criteria](https://dev.to/challenges/hacktoberfest-week3-2026-10-19) weight writing most heavily. Additional decoration cannot substitute for a dependable demonstration and a clear account of what Gemma contributes.

## Evidence and limits

The execution ledger records final test, service restart and real-inference outcomes after integration. Browser access has been intermittent; only checks actually observed on the final artifact are marked complete. No genuine external contributor trial, testimonial, independent human ground truth or measured human savings is claimed. The local DEV draft remains unpublished pending its separate publication gates.

## Final retained engineering evidence

- **130 Python tests and 34 subtests**, including 20 launcher/lifecycle checks, passed. **48 local frontend tests and three replay tests** passed separately. Ruff F/E9, TypeScript/build, diff whitespace and npm audit passed; npm reported zero known vulnerabilities at the recorded check. The existing Starlette/httpx TestClient deprecation warning remains visible. The latest local build ran under bundled Node 24.22.1; earlier setup/CI used the pinned Node 24.19.0.
- Actual macOS services started with parent process ID 1, independent of the chat. A real stop/start cycle restored the identical immutable snapshot and stored decisions, rejected the old token, and reported actual Gemma readiness. Local report: `outputs/service-recovery.json`.
- The initial recovery run exposed a TIME_WAIT port-probe error and asynchronous teardown race. The launchers now check whether a real listener can bind/listen, distinguish active unmanaged listeners, and wait for owned teardown to finish. Regression tests include actual ephemeral TCP connections as well as fake launchd state transitions. The later real recovery cycle passed.
- The actual frontend API adapter completed a rejected-token → single refresh → successful save sequence against the real restarted backend, with the note present in the exported Markdown and the test decision reopened. The integration used explicit connection-close HTTP requests; it is not a browser rendering test. An earlier keep-alive connection failed after restart and was deliberately not replayed automatically, consistent with the safe-retry policy. Local report: `outputs/actual-client-recovery.json`.
- While browser access was available, keyboard navigation opened/imported the real Eventyay PR and started local Gemma; the rendered result showed one pair, nine sources, four excluded automated comments and about four seconds model runtime. The later compact workspace header has not been rendered: access became disabled again, and the user was asked to enable it. No full final mobile/screen-reader/reduced-motion pass is claimed.

The application and model are left running as managed login-session services. The project is still a preview until the remaining rendered and publication gates are satisfied.
