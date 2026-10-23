# ReviewRadar evaluation and evidence plan

Planning baseline · 23 October 2026. No accuracy, time saving, trial participation or benchmark result is asserted by this plan.

## Questions to answer

1. Does the model find concrete review requests that a simple metadata/comment queue cannot distinguish?
2. Does pairing a possible later author response reduce reading effort without falsely implying a fix?
3. Does the interface make incomplete data, historical evidence and uncertainty understandable?
4. Does a real contributor find this useful enough to use again?

Engineering tests, model evaluation and human usability evidence answer different questions. Passing tests cannot establish model precision or customer demand.

## Dataset and provenance

Start with a small authored-public-PR set, including human maintainer requests, later author replies, bot-only discussion, approval after changes requested, open/merged/closed PRs and inline threads. The v1 queue is explicitly human-review only: bot fixtures test preservation, exclusion counts and scope communication, not extraction of bot requests. A promising candidate is not automatically an accepted test case. Fetch current data read-only and record URL, IDs, timestamps, PR head SHA, completeness and retrieval date before selecting examples. Disclose the collection's convenience-sample bias: these are the author's repositories and interactions, not a representative population of all projects.

Use real source text with attribution; fixture notices must distinguish the project's code license from comments authored by other people. Keep publication excerpts minimal. Do not invent missing thread bodies, response times or explanations for a maintainer's decision. Synthetic fixtures test malformed input, injection and rare states; label them synthetic and exclude them from real-world accuracy totals.

Aim for 20–30 independently labeled request opportunities across at least five distinct PRs if the available history supports it. If fewer exist, publish the actual denominator and treat the result as a pilot. Do not create trivial extra rows to reach a number.

## Label protocol

Freeze original raw snapshots. For each evaluation case, record a cutoff time and remove comments created after it **before** inference. Edited comments with `updated_at` after a historical cutoff cannot reconstruct their earlier text; exclude or flag those cases, rather than leaking a later edit into the past. Current thread resolution and PR state may also postdate a historical cutoff: keep them unknown unless the historical state is independently evidenced. Never show later outcomes to the request/response judge.

Label units are individual request spans with stable source ID and exact quote, not entire PRs. One comment may contain two different requests. Required labels:

| Field | Values / instruction |
|---|---|
| Request | Concrete change, question, suggestion, unclear, or not a request |
| Later author response | Exact response ID and quote, or none visible before cutoff |
| Relationship | Directly relevant, partially relevant, unrelated, or ambiguous |
| Follow-up interpretation | Inspect request; possible response to inspect; uncertain |
| Evidence note | Plain-language reason; no inference that a code fix was correct |

An assistant-created provisional label set must say **developer-labeled** or **assistant-labeled**, not independent human ground truth. A second agent's label review can catch mistakes but remains an agent review. An actual participant may adjudicate uncertain cases; only report that participation if it happened. Record disagreements rather than erasing them.

Split by whole PR, not comment, so adjacent replies and repository-specific discussion do not leak into both development and test. Put prompt-development PRs in a declared development set; hold separate PRs for the final frozen run. Eventyay #6104 has already been used for a model proof and failure inspection, so it belongs to development and cannot become a held-out case. If there are too few PRs, use a clearly labeled exploratory result and preserve at least one unseen PR for a final demonstration. Freeze prompt/model before the held-out run. Do not retune on held-out failures and still call it held out; create a new development iteration and report it honestly.

## Comparisons and measures

Run the same cutoff snapshots through:

- **No-model baseline:** a source-linked list of every nonempty human, non-author comment with GitHub metadata. It provides no semantic request or response judgment.
- **ReviewRadar model:** request-span cards and possible response pairs, with uncertainty and citations.

Report exact counts, not a single celebratory score:

| Measure | Definition |
|---|---|
| Citation validity | Valid IDs and exact source quotes / all emitted citation pairs; enforced validity is not semantic correctness |
| Request precision | Correct actionable request spans / model-emitted request spans |
| Request recall | Correct detected request spans / labeled requests visible at cutoff |
| Pair precision | Relevant later author response pairs / emitted response pairs |
| False reassurance | Cases presented as possibly responded despite unrelated evidence; inspect every occurrence |
| Abstention and coverage | Unclear, rejected, timed out and failed PRs / selected PRs; include these denominators, total comments, processed non-bot comments and explicitly excluded bots |
| Local runtime | End-to-end analysis time, model identity, hardware and cold/warm state |

Request matching accepts the same underlying request with a narrower exact quote; it does not require character-identical span boundaries. Document an adjudication rule before scoring. Do not convert model-reported confidence into calibrated probabilities. A baseline comment list does not produce semantic labels, so compare its extra reading burden and usability rather than manufacturing a classifier score for it.

Release floors: 100% accepted citations satisfy mechanical validation; zero invalid source links accepted; no incomplete PR is presented as cleared; each false-reassurance error receives a documented prompt/UI mitigation or remains an explicit limitation. These are safety gates, not a guarantee of accurate triage. If response matching remains unreliable, ship requests-only with later comments displayed as evidence instead of claiming the model solves matching.

## Behavior and failure tests

- Mixed successful and failed PRs, zero cards with failures, rate limits and nested-page caps remain visibly incomplete. A bot-only complete snapshot may have zero eligible human comments; the UI must state that scope and exclusion count, not that all review feedback is cleared.
- Fake source IDs, quote paraphrases, same-time/earlier responses, another PR's reply and response-only output are rejected.
- Multiline exact quotes, Unicode, Markdown, duplicate excerpts, edited/deleted accounts and duplicate comment IDs behave deliberately.
- Comments containing instructions to ignore rules, reveal data, follow URLs or execute commands cannot gain tools or write authority.
- Malformed/imported JSON, very large bodies, model unavailability, timeouts and output truncation produce actionable errors; the baseline is never disguised as a model run.
- Old changes-requested reviews followed by approval do not automatically become current overdue requests. PR merge/closure stays visible without implying verified code quality.
- Local reviewed state persists across restart; it cannot silently mark a card in a different analysis reviewed.

## Real-person trial

Prepare a five-minute guide after a functioning demo exists. Ask a contributor to inspect one small, public or non-confidential PR packet; avoid requesting private discussions. Compare finding an outstanding request with the ordinary GitHub view and with ReviewRadar. Counterbalance order if more than one person participates. Capture the exact task, start/end criteria, errors, participant-reported confusion and whether the result was useful. A narrated demo by the author is **self-test**, not independent validation. Do not invent or extrapolate ROI from one task.

No outreach or repeated pings are needed to manufacture evidence. Recruit through a permitted channel only under the user's existing authorization and channel rules. A person declining or not replying is a recorded outcome, not user validation.

## Evidence artifacts

Keep a dataset manifest, labeling file, frozen prompt, run manifest, machine-readable predictions, scoring report and error ledger. Add SHA-256 hashes for the snapshot and prompt, software commit, model revision, UTC times and mode. Public replay uses an actual saved run with its date and coverage; an edited presentation fixture must be labeled curated and cannot masquerade as raw output. Keep development and evaluation files separate from the user-facing app's local database.

Publish a short limitations paragraph beside the results: small convenience sample; ambiguous review intent; source-state staleness; later author response does not establish a fixed defect; unsupported large PRs; local hardware-dependent runtime. The submission should tell judges what can be tried and what was not independently established.
