# Frozen v10: eight fresh PR discussions

24 October 2026. **Engineering evidence, not independently adjudicated human ground truth or a measurement of saved effort.** This unfavourable result must not be turned into a combined “accuracy” or winner-readiness score.

## Result and implication

All eight first attempts completed and all 26 emitted cards passed the existing source-bound checks. Semantic review against 18 frozen assistant-created ask labels found **16 fully covered asks, one partially covered ask and one missed ask**. The output also contained **four duplicate cards and five cards without a concrete new ask** under the declared rubric. Among the 17 matched ask cards, **15 selected relevant author passages, one selected a wrong passage and one correctly selected no response**. The missed ask had a relevant author response, so response matching cannot be described as covering every expected pair.

This establishes a working source-linked reading aid with meaningful errors. It does **not** establish a reliable work queue, verified fixes or reduced reading effort. The chronology baseline showed 21 reviewer comments; the model emitted 26 cards. Splitting several asks can be useful, but on this set the model did not simply compress the queue, and duplicate/false cards add correction work.

## Selection and freeze

The [protocol](PROTOCOL.md) was written before discussion bodies and predictions were fetched. A fixed list of 80 authored PRs, sorted by latest update, was screened in order until eight complete snapshots with nonempty non-bot reviewer text were found. Eighteen results were screened: nine excluded for no eligible human review and one self-owned repository excluded; no selected case appeared in the four earlier ReviewRadar evaluation PRs or the saved replay. No semantic category or organization quota was imposed.

“Fresh” means new to this ReviewRadar evaluation. The author or earlier OSS contribution agents may already have encountered the underlying discussions. This is not an adversarially secret benchmark or a random sample of GitHub. It contains recently reviewed work from one author, three organizations and related projects, with only one labelled no-response ask. No untouched reserve was selected.

Snapshots, original IDs, capture times and SHA-256 hashes are listed in [the freeze manifest](freeze-manifest.json). Full public histories and raw model output remain in ignored local `outputs/upgrade/evaluation/`; publication uses IDs and paraphrases rather than lengthy third-party text. The [labels](labels.json) were frozen before inference. The parent reviewed selection and ambiguous annotations before authorizing the first run. The labels are assistant-created engineering annotations, not an independent human panel.

Frozen label hash: `eee87456650129d8f751287efdfdff7a2b0f4a3e315f4e7986394e55ace674b4`.

Frozen manifest hash: `1d50ab779fd5ce93d8e0dae1df9b1eb625fcc6ba971b3b261c80d2776072689e`.

## First-attempt case table

| PR, captured 24 October | Labelled asks | Full / partial / missed | Cards | Duplicate / non-ask extras | Wrong response | Model seconds |
| --- | ---: | --- | ---: | --- | ---: | ---: |
| [Eventyay #6581](https://github.com/fossasia/eventyay/pull/6581) | 7 | 7 / 0 / 0 | 8 | 1 / 0 | 0 | 19.058 |
| [Search-a-licious #482](https://github.com/openfoodfacts/search-a-licious/pull/482) | 1 | 1 / 0 / 0 | 1 | 0 / 0 | 0 | 2.295 |
| [WPFAevent #365](https://github.com/fossasia/WPFAevent/pull/365) | 0 | 0 / 0 / 0 | 0 | 0 / 0 | 0 | 0.278 |
| [Teamshifts #229](https://github.com/fossasia/eventyay-teamshifts/pull/229) | 1 | 1 / 0 / 0 | 1 | 0 / 0 | 0 | 2.319 |
| [Exhibition #316](https://github.com/fossasia/eventyay-exhibition/pull/316) | 7 | 5 / 1 / 1 | 10 | 3 / 1 | 1 | 16.720 |
| [Open Food Facts Python #527](https://github.com/openfoodfacts/openfoodfacts-python/pull/527) | 0 | 0 / 0 / 0 | 1 | 0 / 1 | 0 | 1.713 |
| [Apollo3 #867](https://github.com/GMOD/Apollo3/pull/867) | 2 | 2 / 0 / 0 | 2 | 0 / 0 | 0 | 3.769 |
| [JSON Schema Test Suite #1234](https://github.com/json-schema-org/JSON-Schema-Test-Suite/pull/1234) | 0 | 0 / 0 / 0 | 3 | 0 / 3 | 0 | 4.462 |
| **Total** | **18** | **16 / 1 / 1** | **26** | **4 / 5** | **1** | **50.614** |

Times are observed per-PR analysis wall times, including tokenization and the applicable extraction/link calls, not download/setup/reading/decision time. Median 3.044 seconds; range 0.278–19.058 seconds. The baseline reading list takes effectively no inference time; its purpose and outputs differ, so these are not equivalent request-classifier speed or precision metrics. There were no failed or over-budget PR analyses in these eight attempts; this does not remove the existing bounded failure paths.

## Error register

- **Completed actions mistaken for asks:** JSON Schema's maintainer reported three changes already made. The model turned all three into unanswered requests. These are strong false-follow-up examples, despite mechanically valid exact quotations.
- **Support mistaken for a new task:** the Python SDK comment supports adding UTF-8 handling for earlier Python versions, which the PR already does. The model produced one request. A reasonable reviewer could interpret the supportive sentence as an optional suggestion; the frozen concrete-new-ask annotation and this sensitivity remain visible.
- **Repeated asks and empty fragments:** Eventyay repeated the embedded-video ask across reviewers. Exhibition produced separate cards for a general complaint, a bare introductory imperative and overlapping geometry requirements. A literal source quote can be genuine yet fail to express a useful standalone task.
- **Missed colour refinement:** Exhibition's explicit request to retain original outlined action colours was not separately represented.
- **Wrong response association:** Exhibition's test-location ask was paired with a later UI size/colour update. The available earlier author paragraph explicitly describing integration into existing test suites was the relevant answer.
- **Partial geometry extraction:** the compact width/height request and fixed geometry requirement were fragmented into separate cards. Under the frozen grouping, one coupled ask is partially covered and redundant fragments add cards. A different granularity convention changes these counts, which is why the underlying case-level record is retained.
- **Relevant does not mean complete:** the clipping discussion links to investigation and a request for a design decision. That is a relevant conversational response, not a completed UI fix. An Eventyay thread-resolution excerpt likewise reports rechecking; surrounding author text states intent to resolve, but the application does not verify completion.
- **Awkward source partition:** the generic-error request quote begins midway through text containing a translated error sentence. It is exact and bound, but full-source context is needed. Mechanical validity alone is insufficient.

## Transparent scoring addendum

No frozen label was overwritten. Eventyay's generic-error card selected a later inline author passage explicitly retaining the localized fallback. The initial annotation listed other acceptable later author comments but omitted this legitimate alternative. [Case-level scoring](results.json) records that additional accepted source ID and the reason separately. Treating it as a wrong match solely because of the ID list would penalize a semantically relevant answer.

Semantic scoring is not an exact-ID lookup: the selected quote must still address the ask. This is why Exhibition's unrelated test response remains incorrect even though it is from an author update containing valid tests elsewhere in the PR history. The other counter-readings about supportive suggestions and grouping remain documented rather than silently resolved in the model's favour.

## Reproduction and identity

Run `PYTHONPATH=backend .venv/bin/python evaluation/v10-fresh/prepare.py` only to prepare a separately documented capture; it refuses an existing selection log. Do **not** overwrite this frozen set with today's mutable GitHub bodies. The ignored original snapshots, with manifest-verified hashes, are required to reproduce these exact inputs.

Run `PYTHONPATH=backend .venv/bin/python evaluation/v10-fresh/run.py` against those snapshots and the authenticated local model. It refuses existing first-run artifacts; a future separately named run must retain the initial result and be described as replication/regression, not an unseen test. The runner verifies source, label, protocol and model implementation hashes, preserves failure status, and does not write the application database.

[Run identity](run-summary.json): `human-review-passages-v10`, model `reviewradar-gemma4-e2b`, GGUF `8e30dff3ac4c8434c49a7036fa15564bdbb6044e42bf04550bf1a096ad7e6a52`; runtime SHA-256 `330ef197918263288c4017f164154bd11406b6e86d1357b5f83625bb85c10b1e`; 16,384 context, maximum output 2,048 tokens, 1,024-token margin, temperature zero, no retry. The run records actual code, prompt and label hashes.

The model was not tuned after these results. Product correction controls can reduce disagreement friction, but they do not improve these measured extraction or matching results. Any later semantic change needs a separately versioned development protocol; rerunning these exposed cases is regression evidence.

Independent engineering review of scoring is pending until recorded by the parent. No genuine participant feedback, time savings or judging outcome is implied.
