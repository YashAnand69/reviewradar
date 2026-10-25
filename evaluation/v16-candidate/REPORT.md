# v16 extraction-prompt candidate — rejected as default

25 October 2026. **This is a fixed regression study on 20 previously exposed PRs, not a fresh accuracy benchmark, a genuine contributor trial or evidence of saved effort.** All original source and label hashes remain unchanged.

## Decision

The Eventyay6104 four-call diagnosis found that the earlier extraction prompt could recover a request missed by the later prompt. The larger study does **not** justify promoting that prompt combination as a dependable improvement. It retains important missing actions, duplicate/context cards and weak reply matches, while introducing a bot-invocation card in a previously correct zero-card case. The parent rejected v16 as the default and retained v13 with its known limitations visible. No further variants or retries were run in this study.

## Candidate, freeze and execution

The candidate is the exact retained v13 module with only the extraction `SYSTEM_PROMPT` restored from Git `c49f420` (v10 wording) and the version string changed to `human-review-passages-v16`. Actor/source guards, constrained schemas, local binding and the improved response-context prompt are unchanged. The active backend model file was not edited.

The archived implementation and [candidate identity/complete case plan](candidate.json) were frozen at **2026-10-25T15:15:05.782352Z**, before the first call. All three original manifests, label/protocol hashes and 20 snapshot hashes were verified before inference and again after scoring. Every input came from its existing recorded ignored path; no new fetch, favourable substitution, relabel or retry occurred.

The order was the original v10 eight-PR pool, the original v13-final six-PR pool (historical directory `v12-unseen`), then the original v15 six-PR pool. Calls ran serially with an exclusive model slot. All 20 attempts completed and every emitted analysis passed mechanical source/actor/chronology validation. No oversize, truncation, validation or transport failure occurred in these 20 attempts. That does not establish general failure-free behaviour.

The run began at **2026-10-25T15:15:05.784508Z** and finished at **2026-10-25T15:17:31.450751Z**. Actual model analyses and separate chronology baselines remain under ignored `outputs/upgrade/v16-candidate/first-run/`. They were not written to the application's database. The implementation/scoring assistant is the same agent; this is not independent human adjudication. The explanatory [protocol](PROTOCOL.md) was written during the fixed run and is not falsely presented as a prior independent preregistration.

## Results by original pool

The same original labels are scored below. “Partial” includes the compact/fixed geometry action split into two fragments, neither of which independently expresses the full requested condition. A compound card can cover two genuine actions, so action counts and card counts deliberately differ.

| Previously exposed pool | Labelled actions | Full / partial / missed | Cards | Duplicate / non-request extras | Relevant / wrong-or-insufficient / correctly absent primary reply cards |
|---|---:|---|---:|---|---|
| v10-fresh | 18 | 16 / 1 / 1 | 22 | 2 / 2 | 15 / 2 / 1 |
| v13-final | 8 | 6 / 0 / 2 | 8 | 2 / 1 | 3 / 1 / 1 |
| v15-unseen | 8 | 4 / 0 / 4 | 4 | 0 / 1 | 1 / 0 / 2 |

The three pools are heterogeneous convenience samples from one contributor's history. Do not combine these into a population accuracy percentage. All annotations are assistant-created engineering judgements. The total output is 34 cards, including four duplicate and four non-request/context cards. Twenty-six primary cards cover the represented actions; geometry fragments and genuine compound asks explain why card and action denominators differ.

## Every case

Reply columns count only the primary cards selected by request specificity before viewing their selected replies. A duplicate with a better response cannot replace a primary's weak answer. Neither a null reply on a false request nor a mechanically valid citation is counted as a semantic success.

| PR | Labels | Full / partial / missed | Cards | Duplicate / non-request extras | Primary replies: relevant / insufficient / absent |
|---|---:|---|---:|---|---|
| [fossasia/eventyay#6581](https://github.com/fossasia/eventyay/pull/6581) | 7 | 7 / 0 / 0 | 8 | 1 / 0 | 7 / 0 / 0 |
| [openfoodfacts/search-a-licious#482](https://github.com/openfoodfacts/search-a-licious/pull/482) | 1 | 1 / 0 / 0 | 1 | 0 / 0 | 0 / 0 / 1 |
| [fossasia/WPFAevent#365](https://github.com/fossasia/WPFAevent/pull/365) | 0 | 0 / 0 / 0 | 0 | 0 / 0 | 0 / 0 / 0 |
| [fossasia/eventyay-teamshifts#229](https://github.com/fossasia/eventyay-teamshifts/pull/229) | 1 | 1 / 0 / 0 | 1 | 0 / 0 | 1 / 0 / 0 |
| [fossasia/eventyay-exhibition#316](https://github.com/fossasia/eventyay-exhibition/pull/316) | 7 | 5 / 1 / 1 | 9 | 1 / 1 | 5 / 2 / 0 |
| [openfoodfacts/openfoodfacts-python#527](https://github.com/openfoodfacts/openfoodfacts-python/pull/527) | 0 | 0 / 0 / 0 | 1 | 0 / 1 | 0 / 0 / 0 |
| [GMOD/Apollo3#867](https://github.com/GMOD/Apollo3/pull/867) | 2 | 2 / 0 / 0 | 2 | 0 / 0 | 2 / 0 / 0 |
| [json-schema-org/JSON-Schema-Test-Suite#1234](https://github.com/json-schema-org/JSON-Schema-Test-Suite/pull/1234) | 0 | 0 / 0 / 0 | 0 | 0 / 0 | 0 / 0 / 0 |
| [openfoodfacts/open-prices-frontend#2472](https://github.com/openfoodfacts/open-prices-frontend/pull/2472) | 0 | 0 / 0 / 0 | 0 | 0 / 0 | 0 / 0 / 0 |
| [fossasia/visdom#1919](https://github.com/fossasia/visdom/pull/1919) | 2 | 1 / 0 / 1 | 2 | 1 / 0 | 0 / 1 / 0 |
| [fossasia/visdom#1952](https://github.com/fossasia/visdom/pull/1952) | 0 | 0 / 0 / 0 | 1 | 0 / 1 | 0 / 0 / 0 |
| [fossasia/visdom#1929](https://github.com/fossasia/visdom/pull/1929) | 2 | 2 / 0 / 0 | 1 | 0 / 0 | 1 / 0 / 0 |
| [fossasia/visdom#1954](https://github.com/fossasia/visdom/pull/1954) | 2 | 1 / 0 / 1 | 2 | 1 / 0 | 1 / 0 / 0 |
| [fossasia/visdom#1928](https://github.com/fossasia/visdom/pull/1928) | 2 | 2 / 0 / 0 | 2 | 0 / 0 | 1 / 0 / 1 |
| [holoviz/panel#8810](https://github.com/holoviz/panel/pull/8810) | 0 | 0 / 0 / 0 | 0 | 0 / 0 | 0 / 0 / 0 |
| [fossasia/scrum_helper#904](https://github.com/fossasia/scrum_helper/pull/904) | 1 | 1 / 0 / 0 | 1 | 0 / 0 | 0 / 0 / 1 |
| [fossasia/voxbento#717](https://github.com/fossasia/voxbento/pull/717) | 1 | 0 / 0 / 1 | 0 | 0 / 0 | 0 / 0 / 0 |
| [fossasia/voxbento#716](https://github.com/fossasia/voxbento/pull/716) | 1 | 1 / 0 / 0 | 1 | 0 / 0 | 1 / 0 / 0 |
| [fossasia/eventyay#6220](https://github.com/fossasia/eventyay/pull/6220) | 3 | 0 / 0 / 3 | 1 | 0 / 1 | 0 / 0 / 0 |
| [fossasia/eventyay#6219](https://github.com/fossasia/eventyay/pull/6219) | 2 | 2 / 0 / 0 | 1 | 0 / 0 | 0 / 0 / 1 |

## Material findings and comparison

### Original eight-PR pool: same ask coverage, fewer cards, new weak replies

The original v10 report had 16 fully covered, one partial and one missed action, with 26 cards. This candidate has the same action coverage with 22 cards. In particular, it correctly emits no cards for the JSON Schema maintainer's completed-action report, where original v10 emitted three false tasks. The Python supportive-comment false ask remains; its optional-suggestion counter-reading remains documented.

However, Exhibition still misses the explicit outline-color refinement and fragments compact/fixed geometry. Its selected reference-dropdown reply only reports restored outline colors: it does not answer reuse of the Exhibitor form pattern. The fixed-size fragment selects a test/browser-check report mentioning size rather than a passage stating fixed geometry across states. That reply is scored insufficient; a more permissive investigation reading could accept it as weak relevant evidence, but it does not change the other request and reply errors.

The test-organization quote selects the conditional alternative asking for coverage in “that file.” It is scored as the same original ask with its full source context; a strict standalone-quote reading would make this partial rather than full, reducing this pool to 15 full / two partial / one missed. This sensitivity is exposed rather than silently resolving it in the candidate's favour.

Exhibition's bare “Do exactly this” introduction remains a non-request card, and the general rejection duplicates the concrete UI refinements. The long-option reply is a relevant browser/OS-dependent investigation, not an implemented clipping fix. Eventyay's duplicate compound video/thread card selects a video-only reply; its clearer primary cards retain the specific actions. Eventyay's localized fallback reply is the same legitimate alternative source accepted by the earlier scoring addendum; original labels were not rewritten.

Primary-card accounting now explicitly retains both geometry fragments. The earlier v10 summary used a different duplicate/fragment presentation; do not infer an exact extra-card improvement percentage from unlike primary denominators. The raw card-count change and unchanged action coverage are directly reported.

### Original v13 six-PR pool: one recovered action, important misses and a new false ask

Coverage rises from five of eight actions in original v13 to six of eight. The description-template request in Visdom #1928 is now captured with a correct null reply. The two-ask Visdom #1929 compound card remains useful and has a reply explicitly addressing removal and two rendering paths.

The branch-update ask in Visdom #1919 and options-mutation ask in Visdom #1954 remain missing. The primary underflow-warning card still selects a generic test-pass statement that does not report keeping the requested warning. Its duplicate rationale card selects the better warning passage, but scoring does not cherry-pick that favourable reply over the preselected primary. The all-NaN rationale in Visdom #1954 is also emitted again as a duplicate.

A material regression appears in Visdom #1952: the human's `@sourcery-ai review` invocation becomes a task card for the PR author, whereas original v13 correctly emitted zero. This is mechanically source-bound but semantically misdirected. Output rises from five cards to eight, including two duplicates and that false ask. The recovered template request does not erase these failures.

### Original v15 six-PR pool: one recovered procedural ask, four misses remain

Coverage rises from three of eight actions in original v15 to four of eight. Voxbento #716's explicit instruction to check reporter intent is recovered with the relevant later author response. The optional Scrum Helper test-only follow-up and the two-action Eventyay #6219 screencast/green-CI compound card remain represented, with correct null replies.

Voxbento #717's coordinated-ownership objection remains absent; its implicit-request counter-reading is retained. Eventyay #6220 still misses all three explicit future tips (screencast, automated-review follow-through, green CI) and instead emits the sentence describing a competing PR's already-existing screencast. A null response on that context card is not a correct absent-response success.

## Separate exposed live comparison

After the 20-case model slot was released, the parent ran current live WPFAevent #368 and Visdom #1954 through retained v13 and this archived v16 candidate on the same newly captured snapshot. This is an operational comparison outside the fixed 20-PR pool; Visdom #1954 is already exposed, and no separate hidden benchmark or independent label freeze is claimed.

Both analyses completed and emitted the same two **request spans** on Visdom #1954: the unused-bounds request and its all-NaN explanatory duplicate. The earlier options-mutation request remained missed. Both emitted zero cards for WPFAevent #368's approval context. Identical extracted spans are not a claim that every generated rationale or reply was byte-identical. This comparison supports rejecting a broad claim that the candidate repaired the practical omission problem.

- v13 analysis `617dbe50c1bc485fa9d903c752e9365f`, snapshot `e70d607bca13241d0a6201ec57e8f781a1dbe8da5a83fbf5dee5f5ffbef5f31d`.
- v16 analysis `62e2c604654042eaa12c618af2b61402` on that same snapshot.
- Parent outputs are preserved privately as `outputs/upgrade/daily-live-v13-analysis.json` and `daily-v16-candidate-analysis.json`; hashes are in [results.json](results.json).

## Timing and identity

These are observed local pipeline times, excluding installation, GitHub fetch, source reading and human correction. They are not controlled comparative latency or saved-effort measurements. Eligibility fast paths can avoid generation for an empty/acknowledgement case.

| Pool | Pipeline seconds total | Median seconds |
|---|---:|---:|
| v10-fresh | 91.229 | 5.050 |
| v13-final | 35.732 | 6.325 |
| v15-unseen | 18.629 | 4.407 |

- Candidate implementation SHA-256: `5303c8d204d8f8c701a87dc88283ad05913d0d16f605fbc11a6602a4dbd2074c`.
- Combined extraction/link prompt SHA-256: `266012d1aabc71851f54f4e26d0a8702815e39874c25a61e67bd571570c859d8`.
- GGUF SHA-256: `8e30dff3ac4c8434c49a7036fa15564bdbb6044e42bf04550bf1a096ad7e6a52`; runtime binary SHA-256: `330ef197918263288c4017f164154bd11406b6e86d1357b5f83625bb85c10b1e`. Existing files were checked against the pinned manifest.
- Run-manifest SHA-256: `30d2816368da5d54bd2bfb6906b5bf7636088774b979d3a33817c1a33fc6719f`.
- Request mapping, written before reply inspection: `586d93bf2b15c71f4abd85da007e483efa1004ae9b01f2f2a3310a505b83286c`.
- 16,384 context, 2,048 output tokens, 1,024 reserve, temperature zero, original per-HTTP 90-second timeout. The candidate did not add the rejected focused pipeline's cooperative whole-PR deadline.

Exact frozen labels/protocol/source identities, case mapping, relevant alternative replies and counter-readings are in [candidate.json](candidate.json) and [results.json](results.json). Original annotations and predictions remain preserved. No genuine user savings, exhaustive request recall, verified fix, independent human ground truth or winning probability follows from this study.

## Practical release consequence

Retain v13 as the documented experimental model path and keep its failures visible. Make full source inspection, an explicitly selected chronology baseline and saved human next actions work well even when model suggestions are missing or weak. Do not replace an empty model result with another mode silently, imply the source panel repaired recall, or call this rejected experiment a completed model upgrade. The user-facing complete workflow and a genuine contributor trial remain more defensible priorities than another benchmark-driven prompt patch.
