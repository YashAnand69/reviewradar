# v14: first-attempt reserved engineering evaluation

The candidate was frozen at **2026-10-24 19:16:57 UTC** before the root/model developer inspected this pool's identities, discussions or labels. A separate preparation agent declared the protocol, continued the original frozen 80-result GitHub search after the prior capture's verified maximum rank 48, screened ranks 49–77 and selected the first six complete eligible public discussions. Twenty-three entries lacked nonempty non-bot reviewer text; none failed intake. There was no semantic quota, additional search or favourable-output selection. Source histories and labels were frozen before inference.

The run began at 19:24:25 UTC and completed at 19:24:40 UTC. Each case received one first attempt. No retry, model tuning or label amendment followed the predictions. Full discussions and actual predictions remain ignored locally; public documents contain IDs, paraphrases and hashes.

## Independent engineering score

Against **6 labelled requested actions**, v14 fully covers **6**, with **0 partial and 0 missed**. It emits **7 cards**: **5 matched ask cards** cover the six actions because one compound card explicitly covers two requirements, plus **2 duplicate cards**. There are **0 unrelated/non-request extras beyond the duplicates**.

Of the **5 matched ask cards**, **4 select specific relevant later author passages**, covering five actions. The remaining matched card correctly selects **no response** for a design-choice question without a visible later author reply. There are **0 insufficient matched reply spans** in this small reserved run. Relevant author prose does not independently verify a fix or show that the maintainer accepted it.

| PR | Labelled actions | Full / partial / missed | Cards | Duplicate extras | Relevant / insufficient / correctly absent matched reply cards |
| --- | ---: | --- | ---: | ---: | --- |
| Visdom #1917 | 2 | 2 / 0 / 0 | 3 | 1 | 2 / 0 / 0 |
| Visdom #1933 | 2 | 2 / 0 / 0 | 1 | 0 | 1 / 0 / 0 |
| Visdom #1911 | 1 | 1 / 0 / 0 | 1 | 0 | 1 / 0 / 0 |
| PSLab App #3654 | 0 | 0 / 0 / 0 | 0 | 0 | 0 / 0 / 0 |
| Open Food Facts Explorer #2061 | 1 | 1 / 0 / 0 | 2 | 1 | 0 / 0 / 1 |
| Panel #8851 | 0 | 0 / 0 / 0 | 0 | 0 | 0 / 0 / 0 |
| **Total** | **6** | **6 / 0 / 0** | **7** | **2** | **4 / 0 / 1** |

All **six attempts completed**. The independent scorer rechecked frozen snapshot hashes and source-bound validation for every emitted analysis: **seven cards pass**. Mechanical validity establishes exact source/chronology constraints, not semantic correctness. The chronology reading list has eight nonempty reviewer comments and performs no request classification or response matching. Seven generated cards versus eight comments is not a human workload or time-saving result.

Observed pipeline wall time: median **2.459 seconds**, range **0.207–5.720 seconds**, sum **14.300 seconds**. These times include eligibility handling and applicable runtime calls, and exclude installation, participant reading and corrections. They are not a benchmark against the previous differently composed pool or measured human savings.

## What the sources and actual spans show

1. **Undirected graph requests:** Visdom #1917's first reviewer request asks about mismatched edge labels. The selected author span explains preserving first-seen unique input order. Its later separate request asks for an edge-ordering regression; the chosen author span describes interleaved, repeated/reversed and iterator cases in both undirected modes. That is specific relevant evidence. The model also turns the reviewer's explanation of affected duplicate edges into a third card. Under the frozen grouping, that explanation motivates the regression rather than requesting a third action: one duplicate extra remains.
2. **Compound embedding change:** Visdom #1933's one selected passage explicitly requests both dense label normalization and reuse of the same mapping in lasso selection. Its chosen author span describes both changes. This is **one card covering two labelled actions**, not two successful cards and not a missed action merely because the card count is one.
3. **Legacy column-vector behavior:** Visdom #1911's selected request asks to preserve the layout when the row count matches legend length. The author span explicitly describes the legacy one-row, multi-series behavior and distinguishes a single-label matrix. This is relevant to the requested preservation.
4. **Design question split unnecessarily:** Explorer #2061 asks why a modal was introduced and notes that the interaction could have been inline. The frozen labels treat this as **one design-choice request with an alternative**, not two independent required implementations. The model produces a question card and a separate inline-suggestion card. Both correctly have null replies, but the second is counted as a duplicate, not a second successful unanswered action.
5. **Closure versus a new task:** PSLab App #3654 explains closing in favor of another solution and invites possible future testing/contributions. It does not request a current-PR change under the frozen protocol, and the model returns zero cards. A reasonable counter-reading treats the broad testing invitation as an optional general task; this ambiguity is retained, rather than silently changing the primary denominator after seeing the output.
6. **Thanks-only discussion:** Panel #8851 contains appreciation without a requested author action; zero cards is correct under the annotations. One narrow thanks-only case does not demonstrate reliable handling of all approval/status language.

The graph regression's problem description could be treated as a separate bug report, and the modal question and inline suggestion could be split into two semantic units under another protocol. The primary counts keep the predeclared action grouping. These disagreements illustrate why source IDs and card counts alone cannot score request quality; they do not justify relabelling the set to make duplicate cards disappear.

## Provenance, limitations and release meaning

Candidate: `human-review-passages-v14`; implementation SHA-256 `5f4eae1bdf0cc265d2ee16e71e3369c39f9f178cc31e7ac6457656ea7d05d2b1`; prompt hash `174b6945d0f01c7e63228b8ff3c1c926ad7ad6843ef90097e13935ea89817301`. Exact candidate-file, run-manifest, label and protocol hashes are preserved in [results.json](./results.json). Labels SHA-256: `e9a16610d00b063ec0111f5f2248cfcb78c66e4d88eb61d6526e1cef1c52a268`; freeze-manifest hash: `fbac397c932e3362c35dd6b5e25e8e37a1ded27520c5a5a126e6782b5eac5158`.

The same Gemma 4 E2B Q4_0 model and runtime were used: model hash `8e30dff3ac4c8434c49a7036fa15564bdbb6044e42bf04550bf1a096ad7e6a52`, runtime hash `330ef197918263288c4017f164154bd11406b6e86d1357b5f83625bb85c10b1e`, 16,384-token context, 2,048-token output, 1,024-token reserve, temperature zero and a 90-second cooperative whole-PR budget. A blocked read remains bounded by its request timeout; this is not an OS-level hard cancellation guarantee.

These six PRs are all from one contributor; half are Visdom. They are a convenience sample, annotated by an assistant, not independently adjudicated human ground truth. The annotator may have encountered the sources during prior OSS work, but no ReviewRadar predictions for this pool were inspected before freezing. The scorer did not implement the candidate. This is independent engineering checking, **not a genuine participant trial**.

The result supports a narrowly stronger reading aid on this reserved sample. It does **not** establish universal request recall, verified fixes, time saved, a completed real-user trial or a winning probability. The exposed v14 regression still contains one wrong reply match and two rationale duplicates; retain those failures beside this report. This reserved pool is now exposed and cannot be reused as unseen evidence after further tuning.
