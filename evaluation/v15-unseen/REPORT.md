# v15 final experiment: reserved first-attempt evaluation

**This result does not support dependable extraction.** On eight frozen assistant-labelled actions, v15 fully captures **three** and misses **five**. It emits three cards, including one false ask. Fewer cards conceal substantial lost requests, rather than demonstrating a better queue.

The candidate was frozen at **2026-10-24 19:31:26 UTC**, before the root/model developer saw this pool's new discussions or labels. The independent preparation agent declared the exact author/latest-update query with a limit of 160 before new bodies were fetched. GitHub returned 155 results. All identities in the original search80, all previous capture records/manifests, pilot/showcase cases and self-owned repositories were excluded. Of the first 113 examined entries, 81 were prior/self exclusions and 32 were novel screens; the first six complete cases with nonempty non-bot reviewer text were selected. Twenty-six novel cases lacked eligible reviewer text; no intake failed. No additional search, category quota, case swap or favourable-output filtering occurred.

## Independent score

| PR | Labelled actions | Full / partial / missed | Cards | False extras | Relevant / insufficient / correctly absent matched reply cards |
| --- | ---: | --- | ---: | ---: | --- |
| Panel #8810 | 0 | 0 / 0 / 0 | 0 | 0 | 0 / 0 / 0 |
| Scrum Helper #904 | 1 | 1 / 0 / 0 | 1 | 0 | 0 / 0 / 1 |
| Voxbento #717 | 1 | 0 / 0 / 1 | 0 | 0 | 0 / 0 / 0 |
| Voxbento #716 | 1 | 0 / 0 / 1 | 0 | 0 | 0 / 0 / 0 |
| Eventyay #6220 | 3 | 0 / 0 / 3 | 1 | 1 | 0 / 0 / 0 |
| Eventyay #6219 | 2 | 2 / 0 / 0 | 1 | 0 | 0 / 0 / 1 |
| **Total** | **8** | **3 / 0 / 5** | **3** | **1** | **0 / 0 / 2** |

The **two matched ask cards cover three actions**, because one compound card explicitly requests both a screencast and passing CI. Both correctly have no visible later author response. There are **zero duplicate cards**, **one non-request extra**, and **zero matched cards selecting an actual later response**. The two annotated requests that do have relevant later author responses are both missed; therefore no success in matching a visible reply can be claimed from this run.

Six actions have expected null responses; three are captured and three are missed. The false extra also has a null response, but that does not count as a correct absent-response result because the underlying card is not a request.

All **six first attempts completed** and all **three cards passed source-bound validation**. The scorer independently verified frozen snapshot hashes and bound analyses. Exact quotes and chronology therefore remain mechanically valid while task coverage is poor. Pipeline times: median **1.421 seconds**, range **0.001–3.162 seconds**, sum **8.825 seconds**. Eligibility fast paths can avoid model calls; zero-card elapsed time is not necessarily generation time. No measured human savings follows from these timings.

## What failed and what worked

- **Scrum Helper #904:** the optional, specific invitation to preserve this PR's unit tests in a separate test-only PR is captured with a correct null response. The maintainer's statement that the production bug was already fixed is not a new implementation task. Neither the annotation nor the card authorizes reopening the closed PR.
- **Voxbento #717:** the reporter objects that the patch was already privately coordinated and reserved for their own implementation. The frozen annotation treats this as an implicit request to respect coordinated ownership. A later author apology and closure directly address that concern, but the pipeline emits no card. This is genuinely ambiguous: it could be read as a report of past coordination without a literal new request. Keeping that counter-reading does not erase the other misses. If this one annotation were excluded, the result would still be **three covered and four missed out of seven**.
- **Voxbento #716:** the reviewer explicitly asks the author to check reporter intent before taking future issues. This is concrete procedural guidance, not just praise or a generic invitation. The later author apology and stated screening change are relevant responses. The pipeline emits no card, missing an important real collaboration lesson despite its explicit wording.
- **Eventyay #6220:** the model selects a sentence describing the competing PR's existing screencast and narrower scope. It is comparative closure context, not a requested action from the author. Meanwhile it misses the comment's three explicit tips about including a screencast, addressing automated review findings and ensuring green CI. Merely mentioning a screencast in a source does not make that sentence the request.
- **Eventyay #6219:** a single compound card captures both future screencast and CI guidance. Its null response is correct: the earlier author test report precedes the reviewer guidance and cannot serve as a strictly later response. This is one successful card covering two actions.
- **Panel #8810:** thanks-only text correctly produces zero cards. This narrow case does not offset the missed procedural asks in other discussions.

Closed PR state does not erase historical asks or prove compliance in later work. These labels concern source-linked conversation, not current obligations or permission to submit new work. Intermediate focused-extraction and verifier selections are not persisted in the final analysis artifacts, so this scoring cannot attribute every lost ask specifically to the verifier. It evaluates the actual **v15 pipeline**, without inventing an internal causal trace.

## Provenance and release interpretation

Candidate `human-review-passages-v15`; frozen implementation SHA-256 `ccdbe2f2a967de55ef264ea1521b705488d95433fd0a112f85dd163373f5eae8`; labels hash `b65e69912cfd6c289df2fe5b97bcb96cc63cd6e607959490beddeae2fd302bb6`; freeze-manifest hash `ea3acb43b557dcb686f4df4391ab8d10b2dccfb6638832a632040dd2d3ed86eb`; completed run-manifest hash `c873bf00dc2480bb8078a4db2baf7f24880fab33133c4d8d6c2fbce5bbc03d48`. Exact candidate-file and protocol hashes, per-case mappings and counts are in [results.json](./results.json).

Model/runtime identity, context/output limits, temperature and cooperative 90-second budget are preserved in the ignored run manifest. Source histories are in ignored `outputs/upgrade/v15-unseen/`; first attempts are in its `first-run/` folder. No scorer inference, prompt modification, retry or label amendment occurred. Hashes identify frozen v15 artifacts and do not depend on which implementation is later chosen for release.

This convenience sample contains one author's prior OSS discussions, mostly FOSSASIA. Assistant labels and independent agent scoring are not independent human adjudication or a participant trial. Sources may have been encountered during earlier contribution work; they were not used in ReviewRadar model development before this freeze. The result offers no population accuracy, verified-fix claim, measured productivity or winning probability.

The [broader exposed regression](../v15-development/BROAD-REGRESSION.md) removed only one of v14's 31 cards while retaining semantic mistakes and adding runtime work. This reserved result additionally shows substantial missing asks. Preserve both findings if the experiment is rejected; do not select only the successful compound card or describe the verifier as a reliability guarantee. No further semantic tuning follows this final experiment. This pool is now exposed.
