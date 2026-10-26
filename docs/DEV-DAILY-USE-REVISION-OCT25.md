# Published revision — prepared 25 October, saved 26 October 2026

Saved to the existing Week 3 article after preview and verified on its public page on 26 October. The current title, URL, cover, tags, challenge association and Fully Autonomous disclosure were preserved. No second entry. See docs/21-DAILY-USE-UPGRADE.md for release evidence.

<!-- ARTICLE START -->
*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 3: Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19).*

## What I Built

Two reviews on my [Visdom #1954 PR](https://github.com/fossasia/visdom/pull/1954) ask for different things: avoid mutating options that may be reused, and avoid calculating contour limits when those values are unused. A later author reply discusses the changes. When returning to that conversation, I need to recover the specific request, find the relevant reply and decide what to inspect in the diff.

**ReviewRadar prepares that reading session.** Local Gemma proposes reviewer requests beside possible later author responses, with exact source passages attached. I can inspect the context, save a next-inspection note and export a source-linked sheet. The app never writes to GitHub, verifies a code fix or certifies maintainer satisfaction.

For **Slow and Steady**, the intended saving is less context hunting before resuming work. Whether the preparation and correction cost actually saves a contributor effort remains unproven.

### A routine for returning to a PR

1. Open **Saved analyses** and search loaded readings by account, repository, PR number or title. Load older readings when needed. The source capture date is separate from the analysis date.
2. Choose **Check these PRs again**. The importer is prefilled, but fetching is explicit. It creates a new capture; yesterday's reading and notes stay unchanged.
3. Compare each proposed request with its possible reply and full source. Record the next inspection you intend to perform. Marking a card reviewed organizes your reading; it does not approve the PR.
4. Save, return later or export the Markdown sheet. A refreshed capture starts independent decisions, so an old reviewed state cannot quietly apply to changed evidence.

The full local app supports one to five selected public PRs authored by the chosen account. Imported snapshots support offline reading. Private repositories and automatic background monitoring are outside this release.

## Demo

[Try the public historical replay](https://yashanand69.github.io/reviewradar/) · [Read the daily routine](https://github.com/YashAnand69/reviewradar/blob/main/docs/22-DAILY-ROUTINE.md) · [Inspect an exported sheet](https://yashanand69.github.io/reviewradar/example-review-sheet.md).

The public site is saved evidence and saved model output, **not hosted inference or a live inbox**. Choose Original example or Mixed evidence example. Both retain capture dates and coverage limits. Decisions in the replay stay in the browser.

The original Eventyay example shows a screenshot request and a possible author response. The mixed Visdom #1919 example retains an insufficient test-pass reply and a missed branch-update ask. Choose **Reply not relevant**, save your next-inspection note and download the sheet. Your assessment remains separate from the original output.

[![Agent-operated local demonstration of a saved assessment beside unchanged model evidence](https://yashanand69.github.io/reviewradar/mixed-assessment.jpg)](https://yashanand69.github.io/reviewradar/)

### When the model misses a request

The 25 October live check on my open PRs captured 13 source objects across WPFAevent #368 and Visdom #1954. Gemma found the min/max request and a relevant later explanation, but duplicated its all-NaN rationale and missed the options-mutation request. Exact quotations did not make the extraction complete.

That is why the app exposes reviewer comments without a request card. In a zero-card result, **Read reviewer comments without AI** explicitly creates a separate chronology reading list. It includes approvals and context, performs no request extraction or response matching, and supports its own notes, reviewed/reopen choices and export. The original model result stays saved.

An agent-operated HTTP check used that path to retain the original screenshot request, save/reopen a next-inspection note and export it. Another check refreshed my current PR selection and verified that the older snapshot and note were unchanged. These are engineering demonstrations, not a human productivity study.

## Code

[Source, setup and model manifest](https://github.com/YashAnand69/reviewradar) · [Daily-use audit](https://github.com/YashAnand69/reviewradar/blob/main/docs/21-DAILY-USE-UPGRADE.md).

Original application code is MIT licensed. Attributed discussion excerpts, model weights and runtime retain their own rights and terms. The application license does not relicense other people's comments.

## How I Built It

React and TypeScript provide the workbench. FastAPI imports public discussions through the GitHub CLI and stores immutable captures and analyses in SQLite. Human notes and decisions are separate records. Gemma 4 E2B runs through a pinned llama.cpp service on loopback; no GitHub credential is sent to the browser.

Gemma selects existing passage keys for requests and possible later author responses. The app reconstructs exact text and validates source identity, actor and chronology. Each generation checks its actual templated token budget. Oversized or failed inputs remain visibly incomplete. These checks prevent invalid references; they do not establish semantic correctness.

The alternative is a simple chronology of reviewer comments. Gemma's substantive contribution is interpreting asks and proposing response associations. The source-reading path remains usable when that interpretation is wrong.

### What the checks established

The daily-use upgrade fixed a practical history defect: after 100 analyses, older notes still existed in SQLite but their readings disappeared from the UI. Keyset pagination now keeps them reachable, with source-bound titles and dates. New regressions cover tied timestamps, new inserts between pages and preservation of old notes.

The release checks passed **174 backend tests and 34 subtests, plus 71 local frontend and six replay tests**, type/build, focused lint and a dependency audit. Two agents cross-reviewed the daily-use changes. These are structural and workflow checks, not model-accuracy measurements. On 26 October, an agent operated the browser workflow against my actual public PRs: reopened a saved note, marked/reopened it locally, explicitly refreshed the selection, created a separate chronology reading, saved a next-inspection note and downloaded its source-linked sheet. This confirms that bounded flow, not a full accessibility audit or a participant trial.

The [evaluation record](https://github.com/YashAnand69/reviewradar/blob/main/evaluation/REPORT.md) retains missed asks, duplicates and weak replies. In the frozen v13 six-PR study, five of eight assistant-labelled actions were covered. Later candidates were archived rather than promoted. A 25 October controlled diagnosis recovered one exposed request with an earlier prompt, but a broader 20-PR regression retained misses and introduced other errors. The default remains v13 with those limitations disclosed. These small studies use one contributor's history and assistant annotations, not independent human ground truth.

## Why Does Open Innovation Matter?

Open weights let saved discussions be processed locally without a per-request model API bill. Open code makes passage selection, validation, storage and disagreement handling inspectable. The model and reading workflow can be changed independently, and failed experiments can be retained for scrutiny.

This control has a setup cost. The pinned weights are approximately 2.84 GB, with Python, Node and runtime dependencies needed for installation. Fresh GitHub imports require internet. Saved-source processing can run offline after setup. Hardware, electricity and installation still cost something.

The Mac launcher keeps a dedicated Terminal session open. A user-started session was observed healthy, but an actual ChatGPT-quit survival result has not been established. The later session was found stopped; an agent-owned session restored availability for checks. Readiness does not prove permanent availability.

## The Human Role

I supplied my real contribution history, chose the product direction, asked for a free/local workflow and repeatedly challenged usability and premature readiness claims. Those inputs shaped the product. AI agents substantially assisted research, design, implementation, testing and this article; they also operated the engineering examples.

During use, the contributor reads the sources, records disagreement and chooses the actual next action. No model suggestion becomes approval automatically.

A [GitHub trial request](https://github.com/YashAnand69/reviewradar/issues/1) and one [DEV tester invitation](https://dev.to/yashanand69/comment/3ipm6) are published. The [self-guided trial](https://yashanand69.github.io/reviewradar/trial.html) prepares feedback locally without uploading answers automatically. We have no completed independent contributor trial, testimonial or measured time saving. That is the next product test, not something a larger test suite can manufacture.

## Prize Categories

**Overall** and **Best Use of Gemma**. Gemma performs actual request extraction and response association. No category is claimed for an unused integration.
<!-- ARTICLE END -->
