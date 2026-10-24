# Current startup and analysis reliability — 25 October 2026

The new **foreground** startup path avoids submitting the app/model to launchd. Double-click Start ReviewRadar.command in Finder. It preflights, stops exact owned legacy jobs and starts a supervisor in a dedicated Terminal. Keep that Terminal open; Ctrl+C cleans up only that invocation's process groups. Closing the window ends availability. There is no automatic restart or login startup. Legacy launchd `start` is retained for compatibility, not claimed to solve chat-app attribution.

Thirty-nine lifecycle tests passed, including a real disposable wrapper/descendant cleanup test that preserves an unrelated listener. This proves specific cleanup boundaries. It does not prove a user independently launched Terminal and then quit ChatGPT. Native Terminal control is blocked by this chat's computer-control tool; that actual user step is pending. An actual agent-started foreground session reached app/model readiness, stopped its owned child groups on SIGINT, preserved all saved snapshots/analyses/decisions and restored the previous legacy session. That check is recorded privately in outputs/upgrade/foreground-actual.json. It is not an independently user-started quit test.

For the final check:

1. Save your notes; wait for imports/model runs to finish. Double-click Start ReviewRadar.command in Finder and leave its Terminal open.
2. From a second independently opened Terminal in this project, run `.venv/bin/python scripts/probe_local.py --seconds 120` if you want a private availability record.
3. Quit the chat app, then use Safari/Chrome to load `http://127.0.0.1:8893/`, inspect Sources and save/reopen a temporary note. Record actual quit/start/end times and any failure. Reopen the chat app and report the result.
4. Use Ctrl+C in the supervisor Terminal to stop. Test that this stops only ReviewRadar; do not close unrelated applications. The probe records health only, so its output is not alone proof that a quit occurred.

The v14 focused-comment and v15 verification implementations remain archived experiments, not the default. Their local boundary tests did not establish semantic reliability: both retained misses and noise across separate case sets. The retained v13 inference path also returned zero cards in the final fresh Eventyay #6104 API check. The live smoke's request-card assertion therefore failed; the earlier passing smoke is historical evidence, not this release's outcome. See [all results](../evaluation/REPORT.md).

A collapsed source-inspection panel exposes captured human reviewer comments without a request card, including the zero-card case. It is a reading safeguard, not a model fix: comments may be approvals or context, and a source with one card can still contain a missed ask.

The trial page prepares feedback locally, defaults to no quotation permission, and never uploads responses automatically. The participant chooses whether to download/copy/share in the existing GitHub issue. Synthetic form tests and agent demonstrations do not count as genuine feedback. Recruitment and actual participant completion remain separate.

---

## Historical reliability observations (earlier releases)

# Reliability and practical use — 24 October 2026

## Why the page said “action did not finish”

At the start of this audit, neither the app on port 8893 nor the model on port 18085 was listening. The browser retained an older interface, whose network request failed. Earlier successful tests established behavior while the services were running, but did not establish that terminal-bound processes would remain alive after the chat ended. The previous message overstated practical readiness by not separating those two facts clearly enough.

A second recoverability problem was the rotating local session token: after a backend restart, a tab could hold the old token. A third was model configuration being inferred from a credential file alone, despite an unavailable model server.

A later lifecycle check exposed a limit in the initial launchd correction. macOS logs showed the Dock removing jobs attributed to ChatGPT when that app quit. Their process parent being PID 1 did not establish independence from the app that submitted them. The earlier claim that these services would survive closing ChatGPT was therefore unsupported and is withdrawn.

## Implemented corrections

- macOS project-specific login-session services use private ignored configuration/logs and launchd's crash-restart mechanism while the jobs remain loaded. This mechanism does not prevent macOS from removing jobs associated with a quitting application. Nothing is installed as a login-startup item. Start again after logout/reboot.
- Explicit start/status/stop commands, ownership checks and rollback of only newly started jobs. Existing model checksum verification remains mandatory. Unrelated processes are not stopped or replaced.
- `Start ReviewRadar.command` is intended to be double-clicked in Finder and run by the user's Terminal, rather than executed through ChatGPT. It safely stops/restarts only this project's owned jobs so it does not simply reuse jobs attributed to ChatGPT. Starting it interrupts any in-flight import or analysis. Saved database records are preserved; unsaved notes remain only in the open browser tab. **Survival after a full ChatGPT quit under this new launch path has not yet been verified.** A successful start is not evidence of that separate lifecycle property.
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

The execution ledger records test, service restart and real-inference outcomes after integration. Browser access has been intermittent; it recovered for the bounded final-build checks below. These observations do not establish full screen-reader behavior, reduced-motion rendering, every keyboard path or every possible source-body layout. No genuine external contributor trial, testimonial, independent human ground truth or measured human savings is claimed. At that earlier checkpoint the DEV draft was unpublished; the same entry was subsequently published on 24 October.

## Final retained engineering evidence

- **130 Python tests and 34 subtests**, including 20 launcher/lifecycle checks, passed. **48 local frontend tests and three replay tests** passed separately. Ruff F/E9, TypeScript/build, diff whitespace and npm audit passed; npm reported zero known vulnerabilities at the recorded check. The existing Starlette/httpx TestClient deprecation warning remains visible. The latest local build ran under bundled Node 24.22.1; earlier setup/CI used the pinned Node 24.19.0.
- Actual macOS services started with parent process ID 1. A real stop/start cycle restored the identical immutable snapshot and stored decisions, rejected the old token, and reported actual Gemma readiness. Local report: `outputs/service-recovery.json`. This proved restart/recovery while loaded, **not survival after ChatGPT quit**; the later macOS attribution/removal observation supersedes the earlier independence claim.
- The initial recovery run exposed a TIME_WAIT port-probe error and asynchronous teardown race. The launchers now check whether a real listener can bind/listen, distinguish active unmanaged listeners, and wait for owned teardown to finish. Regression tests include actual ephemeral TCP connections as well as fake launchd state transitions. The later real recovery cycle passed.
- The actual frontend API adapter completed a rejected-token → single refresh → successful save sequence against the real restarted backend, with the note present in the exported Markdown and the test decision reopened. The integration used explicit connection-close HTTP requests; it is not a browser rendering test. An earlier keep-alive connection failed after restart and was deliberately not replayed automatically, consistent with the safe-retry policy. Local report: `outputs/actual-client-recovery.json`.
- While browser access was available, keyboard navigation opened/imported the real Eventyay PR and started local Gemma; the rendered result showed one pair, nine sources, four excluded automated comments and about four seconds model runtime.
- Browser access subsequently recovered. The final compact workbench was inspected at desktop size and at 320 px width, with no observed page-level horizontal overflow in the inspected views. The saved-history dialog returned focus to its trigger after Escape.
- A real service stop caused a save to fail visibly while the typed note remained in its editor. Restart, Retry connection and a subsequent save succeeded. This is observed browser recovery behavior; it is not a guarantee against losing an unsaved note when the tab closes or reloads.
- No complete screen-reader, reduced-motion or genuine-user validation is claimed from these checks.

Check current availability with the documented status command; a running login-session job is not a permanently available backend. The project remains a preview. The new user-run launch path still needs its separate ChatGPT-quit lifecycle check, and publication still has its own factual, eligibility and rights gates.
