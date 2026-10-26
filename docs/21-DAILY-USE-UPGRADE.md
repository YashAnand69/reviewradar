# Daily-use upgrade — 25 October 2026

## Product decision

A returning contributor should be able to reopen yesterday's reading, recheck the same public PRs without copying URLs again, inspect exact reviewer comments, save the next inspection they intend to perform, and export a source-linked sheet. Model suggestions may assist that reading; they cannot be its only usable path.

This implements the strongest Week 2 lessons: a short useful workflow, a tangible output, explicit installation cost, and evidence of behavior rather than more decorative features. It does not establish a contest outcome or human time savings. Week 3's official criteria weight writing most heavily and ask what effort the project removes. [Official challenge](https://dev.to/challenges/hacktoberfest-week3-2026-10-19).

## Stages and acceptance gates

1. **Availability and diagnosis.** The browser initially could not connect; both local services were stopped. Logs showed orderly shutdown but did not establish its cause. An agent-started foreground session restored both endpoints. This is not a user-started quit-survival test. Inspect the actual zero-card model path and preserve every diagnostic output.
2. **Return and refresh.** Recognizable saved readings show owner, PR identity/title and source capture date. Local filtering describes its loaded scope. Keyset pagination makes older-than-100 readings reachable. Rechecking a selection prefills an explicit import and creates new immutable evidence; old notes never transfer automatically. Failed refresh preserves the existing reading.
3. **Useful source reading despite missed asks.** An explicit zero-card action creates the existing non-AI chronology reading list. It contains reviewer comments, including approvals/context; it is not an extracted task list. Original model output remains saved. Reading notes, reviewed/reopen and exports work independently for the new baseline analysis.
4. **Verification.** Test cursor identity/order and saved-note reachability; UI regressions for history, refresh failure and explicit baseline selection; full backend/frontend, type/build and bounded live API/browser flow. Use actual authored public PRs; label agent operation separately from genuine participant feedback.
5. **Release and submission.** Publish tested code/replay, record CI/artifact identity, and update the existing DEV entry with actual behavior and unresolved model limits. No duplicate submission, invented testimonial, winning probability or measured-savings claim.

## Current factual audit

- The former saved-history endpoint returned only the newest 100 analyses, with no route to older records in the UI. A temporary-store reproduction retained the old note in SQLite while hiding its analysis from the list.
- History previously showed a model name and opaque ID rather than the PR selection, making repeated sessions hard to identify.
- There was no prefilled recheck action; users had to re-enter their handle/URLs.
- Model-only omitted-source inspection had no obvious way to turn a missed request into a saved reading note. The existing explicitly selected chronology baseline already provides that source-backed workflow; no new model-generated card or human-as-AI claim is needed.
- The disconnected recovery message still recommended the legacy launchd start action instead of the dedicated Terminal launcher.
- The Eventyay screenshot request is present in v13's input and permitted schema. Empty cards are a semantic omission, not a silently filtered source. Earlier passing Eventyay runs were v8–v10; an earlier v13 success on that PR was not established.

## Evidence still required

A genuine contributor completing a trial, net effort compared with direct GitHub reading, a fresh-machine installation test, deeper accessibility checks, and the independent ChatGPT-quit lifecycle result remain separate gates. A bounded current browser pass is recorded below. A public invitation and an agent-operated workflow are not participant feedback. Each result is recorded below only after it occurs.

## Results recorded after implementation

- Backend history now uses bounded keyset pages and an ordered timestamp/identity index. Source metadata is fetched once per unique bound snapshot. Nine regressions exercise 101st-note reachability, tied timestamps, insertion between pages, cursor validation and metadata binding. Full suite: 174 Python tests and 34 subtests passed, with the existing Starlette/httpx warning.
- The frontend implements prefilled explicit recheck, identifiable/filterable history, loading older readings, the explicit non-AI zero-card action, and corrected launcher recovery copy. Five added regressions passed; all 71 local tests and six replay tests passed separately. Type/build and Ruff passed. Two agents cross-reviewed each other's changes and found no correctness blocker.
- Before restarting only the agent-owned foreground session, a consistent SQLite backup and table fingerprints were saved. Snapshots, analyses and dispositions were byte-for-byte equivalent at the table level after restart. A new source-selection import was then exercised separately.
- On actual open WPFAevent #368 and Visdom #1954, live intake captured 13 source objects: six bots and seven human entries, including four nonempty human reviewer comments. Retained v13 emitted one relevant min/max request plus an explanatory duplicate, missed the shared-options ask, and emitted no task for the approval-only PR. This is a real failure, not a successful complete extraction.
- Controlled prompt diagnosis had four frozen first attempts. An earlier prompt recovered Eventyay's screenshot request, but the subsequent 20-case candidate introduced other semantic errors. It was archived and rejected. The active model implementation is unchanged v13; no case was relabelled to make it pass.
- Actual HTTP workflow retained the zero-card model result while explicitly creating a source-backed baseline reading, saving/reopening a next-inspection note and exporting exact source context. A separate two-PR daily reading saved the missed options comment, then refreshed from GitHub into a new capture with independent decisions. The original snapshot, note and export remained unchanged. Cursor navigation reached the history end. The first export assertion incorrectly expected unescaped Markdown; the harness was corrected to compare readable text, with no product change.
- These workflows were agent-operated, not genuine participant trials or measured productivity studies. At the 25 October checkpoint, the rendered-browser flow was not certified: Chrome's accessibility state and screenshot disagreed during an attempted history check. The user was asked to leave Chrome idle while API checks continued. Prior browser screenshots are not treated as proof of this upgrade.

Private operation evidence lives under ignored `outputs/upgrade/daily-functional/`, `daily-restart/` and the diagnostic directories. Public candidate reports retain implementation/input identities and unfavourable results. The later deployment/post checkpoint is recorded below; no full winning, model-completeness or independent quit-survival claim is made.

## Release and browser checkpoint — 26 October 2026

- Source `42c727be098bb19230da073959a7cb01db103b27` passed [the source workflow](https://github.com/YashAnand69/reviewradar/actions/runs/40207654117). The replay commit `d2a89ceec4bc00deb85d42f61b220935341e4472` passed [Pages deployment](https://github.com/YashAnand69/reviewradar/actions/runs/40207697499). All 11 publicly served replay files were compared byte-for-byte with the built artifacts and matched. This verifies the saved replay, not hosted inference.
- In-app browser control became available again. Saved history loaded 23 recognizable readings. Filtering by PR #1954 reopened the older `cbe438fa4502…` reading and its exact saved options-inspection note. Mark reviewed and Reopen both saved locally. No GitHub action was sent.
- Check these PRs again prefilled the two actual public URLs and account. Explicit import produced a new complete capture dated 26 October, 11:55 IST. Choosing the chronology baseline created `604da0b55ad9…` with independent, empty decisions. A new note was saved through the browser; the downloaded Markdown sheet retained its text, original source URL, capture date and uncertainty. The older note remained separate.
- Restoring the known zero-card model analysis `879653101849…` visibly said that no cards did not prove no work remained. Its explicit no-AI action created a separate two-comment baseline `920bab713b46…`, including the screenshot request and an approval. The original model reading remained in history. This is a usable source-reading path, not a repaired model prediction.
- The history dialog closed with Escape and returned focus to Saved analyses. No app console warnings or errors were returned in this bounded browser pass. A requested 320-pixel viewport override did not actually apply: observed inner width was 753 pixels, document width 738, with no horizontal overflow in the checked view. The saved image is not presented as a 320-pixel verification. A full current mobile/screen-reader audit remains unperformed.
- The existing DEV entry was revised in place, previewed and saved. The public page showed Edited on 26 Oct, the new real-PR opening, daily routine, current checks and model limitations. The title, canonical URL, challenge association, tags and Fully Autonomous disclosure were preserved. No new entry or additional tester invitation was created.

Browser evidence and the downloaded sheet are retained under ignored operation outputs. These were agent-operated engineering checks. No independent user trial, measured effort reduction, flawless extraction or contest outcome is claimed.
