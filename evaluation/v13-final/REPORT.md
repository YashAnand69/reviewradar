# v13 final candidate: first-attempt reserved engineering evaluation

Run on 24 October 2026, 17:08 UTC. The final candidate was frozen at 17:04:28 UTC before the reserved discussion bodies were read. The input pool had been captured for v12; v12 was rejected on exposed development results before this pool was annotated or predicted. The amendment and original capture hash are retained in [the reserved protocol](../v12-unseen/PROTOCOL.md). Labels were frozen before inference. All six cases were run once, without retries or further tuning.

This is assistant-labelled engineering evidence, not independent human ground truth, a random sample, measured time savings or evidence of winning probability. It is the first candidate evaluation on this pool; it does not make the earlier v11 reserved set unseen again.

## Independent scoring result

Against **8 labelled asks**, the final output contains **5 fully covered asks and 3 missed asks**. There are **5 cards**: four cards represent those five asks because one genuine compound card covers two labelled asks; the fifth card repeats the rationale for an already represented request. There are **0 unrelated/non-request extras** beyond that duplicate rationale card.

Of the **4 matched ask cards**, **3 select relevant author passages and cover 4 asks**; **1 selects insufficient generic test-pass evidence for its technical ask**. Counting both card and ask denominators avoids treating the two-ask compound card as either a duplicate or a missing task. The only labelled ask without a visible later author response was missed, so this run provides no correct absent-response selection to count.

| PR | Labelled asks | Fully covered / missed | Output cards | Duplicate extras | Relevant / insufficient matched response cards |
| --- | ---: | --- | ---: | ---: | --- |
| Open Prices Frontend #2472 | 0 | 0 / 0 | 0 | 0 | 0 / 0 |
| Visdom #1919 | 2 | 1 / 1 | 1 | 0 | 0 / 1 |
| Visdom #1952 | 0 | 0 / 0 | 0 | 0 | 0 / 0 |
| Visdom #1929 | 2 | 2 / 0 | 1 | 0 | 1 / 0 |
| Visdom #1954 | 2 | 1 / 1 | 2 | 1 | 1 / 0 |
| Visdom #1928 | 2 | 1 / 1 | 1 | 0 | 1 / 0 |
| **Total** | **8** | **5 / 3** | **5** | **1** | **3 / 1** |

All **6 attempts completed** and all **5 emitted cards passed mechanical source-bound validation**. The chronology reading list contains **9 reviewer comments**, but performs neither request extraction nor response matching. Observed per-case pipeline wall time: median **3.247 seconds**, range **0.231–5.447 seconds**, total **16.801 seconds**. These timings include applicable eligibility fast paths and model calls; they are not necessarily generation times for zero-card cases and exclude installation, reading and correction.

## Substantive findings

1. **Missed branch update:** Visdom #1919 explicitly asks the author to update the branch, and a later author update reports doing so. No card represents this procedural request. It is a real miss under the frozen protocol; procedural work cannot be silently excluded after the fact.
2. **Insufficient warning response:** the underflow-warning request is extracted, but its selected author quote only states that a test fails before the change and tests now pass. It does not describe keeping the requested warning. An earlier author paragraph explicitly reports warning when a finite nonzero vector becomes zero; that would be the relevant evidence. The chosen later inline comment discusses warning location in surrounding text, but its selected passage alone is generic. Exact quoting and a later author source do not make this a technically sufficient answer.
3. **Useful compound extraction:** Visdom #1929 puts removal of an unnecessary statement and preservation of two-path test coverage in one request passage. The chosen response explicitly reports both. This is one card covering two distinct labelled requirements, as the frozen ambiguity policy allows.
4. **Missed options immutability:** Visdom #1954's earlier request to avoid mutating the caller's options object is absent, even though a concrete later author response is available.
5. **Duplicated reason:** Visdom #1954's unused contour-reduction request is represented correctly, then its all-NaN warning rationale becomes another card. The warning explanation supports the same requested reduction change; it is not a second distinct ask. This extra card also overstates what passing regressions imply about resolution.
6. **Missed PR template:** Visdom #1928's explicit description-template request has no later author response in this snapshot and is omitted. The keyed-legend request is represented with a relevant response. The absent template card prevents any claim that all unanswered work is surfaced.
7. **Correct zero-card context:** the two no-ask PRs contain human bot invocations rather than requested changes from the author. Both correctly produce zero cards. This is a small, narrow success; it does not establish general handling of praise, agreements or ambiguous status updates.

## Identity, provenance and bounds

Candidate: `human-review-passages-v13`; implementation SHA-256 `24caf2b5b4713df24641ebf6c6b66b846e28893bf5aa5900ad66580530bcba47`; prompt SHA-256 `c842fd59d779305c43799569d343dac9d8b82ff3ec795f237c169b4d29dba5d7`.

The unchanged [reserved labels](../v12-unseen/labels.json) hash is `5b7b4453e2ee5aa28e4c7f58dfd07c1f4a1ddcd8a2d304e8a74cac4faa67d365`; [freeze manifest](../v12-unseen/freeze-manifest.json) hash is `6857d0466ebb3b55503763fa323deb0e8843a02f7de7404b677ccfb2f1c3ba0b`. The directory retains its historical `v12-unseen` name; the actual evaluated candidate is v13, not v12. The input protocol records that distinction.

The fixed original search order was continued from rank 31. Eighteen entries were screened until the first six eligible complete public PR discussions were selected. Five selected PRs are Visdom, so this convenience pool strongly overrepresents one project and one author's maintenance style. The author may have encountered these sources during previous OSS work. No semantic quota or favourable-prediction filtering was applied. Sources were captured around 16:45 UTC, before annotation and predictions; full source hashes and capture timestamps are in the manifest.

Model: Gemma 4 E2B Q4_0, GGUF SHA-256 `8e30dff3ac4c8434c49a7036fa15564bdbb6044e42bf04550bf1a096ad7e6a52`; runtime SHA-256 `330ef197918263288c4017f164154bd11406b6e86d1357b5f83625bb85c10b1e`; 16,384-token context, 2,048-token output, 1,024-token reserve, temperature zero. Actual predictions, per-case metadata and latency remain in ignored `outputs/upgrade/v13-final-unseen/`.

The scorer did not implement the candidate and inspected the preserved output against frozen labels. Original labels and predictions remain unchanged. This independent engineering review agrees with the parent's reported counts, including the compound-card denominator and insufficient generic test-pass response. It is not an independent human panel. After scoring, this pool is exposed; a later model change can only yield regression evidence here.

## Release interpretation

v13 remains a source-linked **reading aid requiring human inspection**, not an exhaustive task list or fix verifier. The finite test shows meaningful requests can be missed and a later author passage can be too weak. Local disagreement controls help users record those judgements; they do not erase measured errors. Zero-card or mechanically complete analysis must not be described as proof that no review work remains.

Retain all earlier v10/v11 results and the rejected v12 experiment. Do not publish only the successful compound example or fewer-card count. Any public summary should report the three missed asks and insufficient response evidence alongside the working example, and should not claim dependable task recall, validated code changes, time saved or a general improvement percentage.
