# ReviewRadar: five-minute first-use guide and comparison protocol

Status: prepared 23 October 2026; **no participant trial has yet been conducted through this guide**. Do not turn this document, engineering labels or an agent-operated browser session into a testimonial or human time-saving result.

## Short guide to share with a volunteer

ReviewRadar prepares an evidence queue from selected public GitHub PR discussions. V1 analyzes human review only; automated messages stay available in Sources and are counted as excluded. It shows possible human requests and later author responses; it does not verify fixes or change GitHub. We are testing whether it makes the discussion easier to reconstruct.

Use the public historical sample first. You do not need to install a model or sign into GitHub. Please do not paste private, confidential or sensitive material. The sample is historical, not your live notifications.

1. Open a sample and tell us, in your own words, what the app is helping you do.
2. Choose one proposed request. Identify exactly what was asked and whether there is a relevant later response. Open the original source if needed.
3. Explain whether the app has established that a code fix works. The intended answer is that it has not; a response is evidence to inspect, not proof of a fix.
4. Mark the item locally reviewed, then reverse that choice. Explain whether anything changed on GitHub.
5. Export the work list. Is it useful enough to return to? Name the first confusing or unnecessary part.

Please report any missing request, misleading match or action you could not find. “I would still use GitHub” is valuable feedback. You can stop whenever you want. We will ask separately before quoting your name or feedback publicly; no response is treated as endorsement.

## Rigorous comparison, if time permits

The short guide tests comprehension; it does not measure saved effort. A comparison needs additional time and the same task definition across conditions.

### Preparation

- Record participant role and prior familiarity with the PRs. One author testing familiar threads is useful first-use evidence but not an independent-user performance study.
- Prepare comparable frozen public PR sets, including actual requests, already-answered requests, optional suggestions, approvals, bot notices and ambiguous cases. Bot notices test source visibility and explicit exclusion, not bot-request recall in the human-review queue. Eventyay #6104 is development-only because the team has already inspected its first failed model output; use different whole PRs for any untouched holdout. Match approximate discussion length/complexity; avoid displaying the same discussion in two conditions to one person, because memory would favor the second condition.
- Freeze manual engineering labels before model predictions. Preserve true uncertainty and multiple legitimate interpretations rather than forcing one unquestionable answer.
- Use three methods if the participant has time: original source reading; deterministic state/chronology queue; model-assisted queue. Rotate condition order across participants or matched sets, recording the order and allocation. With only one participant and few sets, describe the comparison as exploratory and confounded by task differences.
- Do not coach the participant about hidden answers. Offer identical task instructions and source access for all methods. Start timing after common orientation; record setup/orientation separately.

### Identical task

“Identify each concrete request that may still need your inspection. Find a relevant later author response where present. For every item, give the source evidence, say what remains uncertain, and decide whether you would inspect, defer or consider it reviewed locally. You are not required to verify code fixes.”

Record raw reading time, source-opening time and correction time until the participant says the prepared list is usable. Count model waiting and active effort separately; also report total elapsed time. An unattended model run may reduce active effort without reducing elapsed time. A model error or correction is part of the result, not an exclusion after seeing the answer.

### Scorecard

| Field | Record |
| --- | --- |
| Date, app release, snapshot/analysis IDs | Exact values |
| Participant and consent | Anonymous ID by default; role, relevant experience, permission scope |
| Method/order/set | Manual, baseline or model; assigned order and PR IDs |
| Prior familiarity | None/some/authored; explain |
| Setup/orientation | Seconds and assistance needed |
| Active inspection | Seconds, including opening original sources |
| Waiting | Seconds, model or network |
| Corrections | Seconds plus actual edits/decisions needed |
| Total elapsed | Seconds from start until usable list |
| Human requests expected/found/missed | Counts and source IDs; optional/unclear separately; automated sources counted as excluded |
| False reminders | Item IDs and why they should not have been raised |
| Response association | Correct/incorrect/uncertain pairs with source IDs |
| Full conversations still read | Count out of total; not just UI row count |
| Comprehension | Historical versus live, response versus fix, local versus GitHub action |
| Friction and usefulness | Participant's actual words with consent; retain negative feedback |

Do not publish a named quote without the participant's permission. Store only necessary trial notes locally; do not commit contact details. If a participant imports their own data, obtain permission separately before sharing screenshots or source snippets publicly.

## Reporting

For each method report actual case count, participant count, misses, false reminders, uncertain cases, correction burden and time. Show per-participant/per-set values; do not hide a failure behind an overall average. Avoid statistical significance claims with this small exploratory study.

An engineering target is lower total inspection/correction effort, no labelled actionable request omitted from the proposed action/unclear view, and fewer discussions needing complete rereading. The previously proposed 30% target is not an achieved result or an official contest threshold. A failed target should drive a specific change or a narrower claim.

If no real person completes the guide, report: **“No genuine user trial conducted; available evidence is engineering evaluation and browser checks.”** If a person only tries the sample, report comprehension/usability observations and do not infer a numerical savings percentage.

## Feedback-to-fix loop

1. Save a reproducible issue with release/snapshot ID, expected versus observed behavior and impact.
2. Verify against original source before changing interpretation.
3. Fix a bounded issue; add an appropriate regression check.
4. Repeat the affected task, keeping pre-fix and post-fix findings distinct.
5. Update release notes and article claims only from observed results.

No outreach is sent by this document. Any recruitment or external message uses only an authorized channel and actual recipient; avoid repeated unsolicited maintainer requests.
