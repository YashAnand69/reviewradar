# Exposed-case extraction diagnosis: prompt × PR title

25 October 2026. **This is a four-call development ablation on one already inspected PR, not a fresh accuracy evaluation, an independent human trial, or a promoted model version.** The `v16-diagnosis` directory names this investigation; no v16 production prompt was introduced.

## Question and result

The final live Eventyay #6104 run returned zero cards despite retaining the screenshot/video request. Was the source omitted or rejected by local validation? Did adding the PR title explain the change from earlier successful runs?

A read-only inspection found that the reviewer request was present in the message payload, allowed schema enum and local eligibility set. It did not match the acknowledgement guard. Successful validation cannot silently drop that sole distinct candidate. The old live result therefore reflects an empty model extraction, rather than removal by source validation. The runtime log's ten generated tokens and normal completion are consistent with that result.

In the predeclared two-by-two experiment below, the **whole extraction prompt** was the observed factor: the v10 prompt selected the expected source both with and without a PR title; the v13 prompt emitted no cards in either condition. Title inclusion did not change the selection on this source. This does not isolate a particular sentence inside the prompt or establish behaviour on other PRs.

## Controlled method

- Input: the already exposed, complete Eventyay #6104 snapshot captured on 24 October, with nine source objects, five human entries and four bots. The nonempty human reviewer sources are the screenshot/video request and a later approval; another approval has an empty body. Bots remain in the snapshot but are excluded explicitly from model input.
- Fixed source, actor checks, passage partition, constrained schema, binding and model settings from the retained v13 implementation. Only extraction `SYSTEM_PROMPT` and inclusion of the `pr_title` field varied. The v10 prompt was read from Git revision `c49f420` using Python AST; the historical v10 implementation was not substituted wholesale.
- Fixed order: v10/title, v10/no-title, v13/title, v13/no-title. All four full request plans were saved before the first generation. Each cell had one attempt and no retry. All four outputs were saved before inspecting their selections.
- The actual templated-token check and existing output parser ran for every call. Budget: 13,312 input tokens; maximum output 2,048; margin 1,024; context 16,384; temperature zero. No response-linking call was performed.
- Model calls were serial under an exclusive model-call slot. No app database writes, service restarts, active backend edits or default-model promotion occurred.

The plan was frozen at **2026-10-25T15:11:54.641815Z**; all calls finished at **2026-10-25T15:11:58.934430Z**. Raw messages, schema, HTTP responses, timings, runtime inventory, bound candidates and the script are retained under ignored `outputs/upgrade/v16-diagnosis/`.

## All first outputs

| Extraction prompt | PR title supplied | Selected request passages | Local binding | Wall seconds | Completion tokens |
|---|---|---|---|---:|---:|
| v10 | Yes | `review:5396298833/p0` | One candidate, source valid | 1.650 | 92 |
| v10 | No | `review:5396298833/p0` | One candidate, source valid | 1.641 | 92 |
| v13 | Yes | None (`cards: []`) | Zero candidates | 0.650 | 10 |
| v13 | No | None (`cards: []`) | Zero candidates | 0.331 | 10 |

All four ended with `finish_reason: stop`; none was over budget, malformed or truncated. The selected source is the review requesting video/screenshots. Neither v10-prompt cell selected the approval passage. This limited semantic interpretation was made by an assistant, not an independent human label panel.

Input tokenization lengths were 673, 658, 771 and 756 respectively. The runtime reported prompt token counts one higher, reflecting its own accounting; both sets of measurements are retained. Cached-prefix counts varied by cell (0, 364, 0 and 462); this experiment was not counterbalanced or repeated. Timings are individual local observations, not speed claims or time saved by a person.

## What follows, and what does not

The later extraction wording should not be described as a uniformly safer or more reliable improvement. On this exact exposed source it suppressed a genuine historical ask. The source-reading panel helps someone inspect the omission but does not repair the model's recall.

A narrow proposed follow-up is to restore the earlier extraction prompt while retaining current local source/actor constraints and improved response-context matching, then freeze that candidate **before** a separately selected evaluation. However, the [v10 eight-PR report](../v10-fresh/REPORT.md) also retains duplicates, non-ask cards and a wrong response. Restoring its extraction wording cannot be assumed to cure those errors. No production change is justified by this one-case result alone.

A different prompt wording or per-comment classifier would likewise need an explicit new candidate and evaluation, not ad hoc tuning followed by calling these cases fresh. The four planned calls completed; no further prompt variations were tried in this investigation. Previous frozen predictions and labels remain unchanged.

The daily-use workflow must remain able to inspect full sources, make explicit human decisions and retain notes independently of model extraction. A successful API call or exact source citation is not proof that the model found every ask or paired a useful reply.

## Identity and evidence limits

- Retained v13 implementation SHA-256: `24caf2b5b4713df24641ebf6c6b66b846e28893bf5aa5900ad66580530bcba47`.
- v10 system prompt SHA-256: `5e39e9196b62d47856b1c7371432c7ae9658a90b103044e4e1a8a5afd8c1278d`.
- v13 system prompt SHA-256: `c8f680c697e1e64226a226b4ded27f94bbe9e4ed347c21dbe7fe1466113df222`.
- Original snapshot-file SHA-256: `0e96fb3e3d20f6e49e609bb86c9cac7c8adf48a619d1f0f1544aa930c34954d1`.
- Snapshot ID: `429093882aaaf11a7e6fe52c30529642fbfcd42e7d71dc088b94eb065351bc68`.
- GGUF SHA-256, verified against the existing file: `8e30dff3ac4c8434c49a7036fa15564bdbb6044e42bf04550bf1a096ad7e6a52`.
- Runtime binary SHA-256, verified against the existing file: `330ef197918263288c4017f164154bd11406b6e86d1357b5f83625bb85c10b1e`.
- Frozen four-cell plan SHA-256: `2b824bc7bc1cc57560057b7c82745865fef17494ee7592ccd179efd0e7968673`.
- Complete raw result bundle SHA-256: `3863c6b1b71c920d2bf5e264c823d2b88fea4ac560f2c8fdbf3a5c5b4c0c718d`.

The live source is [Eventyay #6104](https://github.com/fossasia/eventyay/pull/6104). A new GitHub fetch is mutable and not the frozen capture. Raw long discussions are deliberately not redistributed with this report. The hashes and preserved local artifacts allow this specific investigation to be audited; they do not make it a population benchmark or a complete public replication package.
