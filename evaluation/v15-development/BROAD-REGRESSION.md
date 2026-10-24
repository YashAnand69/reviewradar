# v15 final verifier experiment: broader exposed regression

The v15 candidate was frozen at **2026-10-24 19:31:26 UTC**, before this run. It adds a selection-only verifier over the already source-bound focused extraction candidates. The verifier cannot invent indices or rewrite quotes. That trust boundary does **not** make the model's semantic choices correct.

The same eight exposed v10 cases and unchanged 18-action annotations were run once. No retry, label amendment or case replacement occurred. The independent scorer rechecked all frozen snapshot hashes and all 30 emitted cards using the bound-analysis validator, then inspected actual request and reply spans. Full source histories and predictions remain ignored in `outputs/upgrade/v15-broad-regression/`.

## Score and comparison

Request coverage is unchanged from v14: **17 fully expressed labelled actions, one geometry action fragmented across two partial cards, zero wholly missed actions**. There are **30 cards**: **19 primary request cards** representing 18 labelled actions, **4 duplicate extras**, and **7 non-request/context extras**. The chronology list contains 21 reviewer comments and performs no semantic classification. This output is not a smaller queue or evidence of time saved.

Primary response scores are also unchanged: **16 relevant reply cards**, **2 insufficient/unrelated reply cards**, and **1 correctly absent reply**. The 16 relevant cards cover 15 labelled actions because one action has two geometry fragments. Source-bound conversational evidence does not independently verify a fix.

| PR | Labelled actions | Full / partial / missed | Primary cards | Duplicate extras | Non-request extras | Total cards | Relevant / insufficient / correctly absent primary reply cards |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| Eventyay #6581 | 7 | 7 / 0 / 0 | 7 | 1 | 1 | 9 | 5 / 2 / 0 |
| Search-a-licious #482 | 1 | 1 / 0 / 0 | 1 | 0 | 0 | 1 | 0 / 0 / 1 |
| WPFAevent #365 | 0 | 0 / 0 / 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 |
| TeamShifts #229 | 1 | 1 / 0 / 0 | 1 | 0 | 0 | 1 | 1 / 0 / 0 |
| Exhibition #316 | 7 | 6 / 1 / 0 | 8 | 3 | 2 | 13 | 8 / 0 / 0 |
| Open Food Facts Python #527 | 0 | 0 / 0 / 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 |
| Apollo3 #867 | 2 | 2 / 0 / 0 | 2 | 0 | 1 | 3 | 2 / 0 / 0 |
| JSON Schema Test Suite #1234 | 0 | 0 / 0 / 0 | 0 | 0 | 3 | 3 | 0 / 0 / 0 |
| **Total** | **18** | **17 / 1 / 0** | **19** | **4** | **7** | **30** | **16 / 2 / 1** |

The verifier removes **only the bare image-attachment URL card** from the 31-card v14 output on this corpus. It does not remove the repeated request cards, generic wrapper, vague reaction, orphan abbreviation fragment or three completed-maintainer actions. A one-card reduction on an exposed small set is weak evidence for the additional stage, not proof of dependable semantic verification.

All **8 first attempts completed** and all **30 cards passed mechanical validation**. Wall time: median **4.253 seconds**, range **0.210–25.446 seconds**, total **62.448 seconds**, versus 59.664 seconds for v14. These are single-run observations, not a controlled performance benchmark, and exclude human reading and correction.

## Card mapping and retained errors

The same request-based primary mapping policy as the [v14 broad report](../v14-development/BROAD-REGRESSION.md) applies: choose the clearest nonredundant request representation before inspecting its response; count a repeated compound card as one extra even when it overlaps two actions. A compound card cannot be credited for requirements its actual quote does not contain.

- **Eventyay #6581:** primary indices **0–4, 7 and 8**; duplicate **6**; non-request wrapper **5**. The alert-role request still selects generic browser-trace text; the readonly-detail request still selects unrelated Node-glob text. Their generated explanations cite other surrounding material instead of proving that the selected quote is relevant. Duplicate 6's video reply does not address its combined unresolved-review portion. The recheck reply is conversational follow-through, not proof that GitHub threads were resolved. The generic-fallback response uses the legitimate alternative inline source already recorded in the original v10 scoring addendum; labels remain unchanged.
- **Exhibition #316:** primary indices **0, 2, 4, 5, 8, 9, 10 and 11**; duplicates **1, 3 and 6**; non-request wrapper/vague reaction **7 and 12**. The only removed v14 card is the attachment URL. Compact dimensions and equal geometry still appear in two separate partial request cards rather than one complete acceptance-criteria card. The long-option response remains a relevant investigation and tradeoff discussion, not a completed clipping fix. Some duplicate-card replies now select a more relevant author sentence, but that does not remove the duplicate task or improve the primary-response denominator.
- **Apollo3 #867:** primary **0 and 2**; non-request fragment **1** remains, produced by splitting the abbreviation before its following noun.
- **JSON Schema Test Suite #1234:** all **three cards are false asks**, quoting changes the maintainer says they already completed. The verifier retains them. Their null replies do not make them outstanding author tasks.
- **Search-a-licious #482:** the optional specific follow-up is retained with a correct null response.
- **TeamShifts #229:** the screencast request selects a relevant author report.
- **WPFAevent #365 and Open Food Facts Python #527:** both correctly return zero cards under the frozen labels. The latter retains its documented alternative supportive-suggestion reading.

## Identity and limits

Candidate `human-review-passages-v15`, implementation SHA-256 `ccdbe2f2a967de55ef264ea1521b705488d95433fd0a112f85dd163373f5eae8`; combined prompt hash `ca6e0aab9e16fab39aa57accf9547f50276cec10d3d0423cedbacb6fda0a03f7`; frozen v10 labels `eee87456650129d8f751287efdfdff7a2b0f4a3e315f4e7986394e55ace674b4`; source manifest `1d50ab779fd5ce93d8e0dae1df9b1eb625fcc6ba971b3b261c80d2776072689e`; completed run-manifest hash `6afa447ec4762a3970ea9d6e1cfcc54b8fb82db638ea6e2c7526b52f80d7490b`.

Model/runtime artifacts and generation settings are unchanged and recorded in the run manifest. The verifier shares the cooperative 90-second whole-PR budget, 12-focused-comment/40-candidate caps and real token checks; no stage silently drops input when a limit fails. A blocked read still uses its configured timeout, not OS-level hard cancellation.

This is exposed engineering regression evidence from one author's convenience sample with assistant annotations and independent agent scoring. It is not independent human adjudication, a participant trial, a verified-fix result, measured productivity or a winning probability. Do not present the verifier as an accuracy guarantee, and do not suppress this larger corpus beside a favourable new reserved result. No further semantic experiments are part of this final candidate evaluation.
