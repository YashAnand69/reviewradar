# v14 broader exposed regression: hard cases remain

This is the frozen v14 candidate's first attempt on the **already exposed v10 eight-PR corpus**, not a new unseen test. No labels were changed, cases replaced or calls retried. The run completed on 24 October 2026 from 19:25:44 UTC. The independent scorer inspected actual selected request/reply spans and checked all eight frozen snapshot hashes and bound analyses without running inference.

## Result and denominator policy

Against **18 frozen labelled actions**, **17 have a fully expressing request card**, **1 is fragmented into two partial cards**, and **0 is wholly missed**. The fragmented action requires both compact dimensions and fixed geometry across states: one card quotes reducing width/height and another quotes fixing size across states; neither alone includes both frozen acceptance criteria. The information is present across cards, but this is **not 18 fully captured single-card actions**.

The pipeline emits **31 cards**, compared with 21 comments in the chronology reading list. **19 primary request cards** represent the 18 actions, including the two fragments for one geometry action. There are **4 extra duplicate cards** and **8 non-request/context extras**. More output and coverage do not establish a clearer or shorter queue.

For semantic scoring, primary cards are selected by the clearest nonredundant request wording, before judging their response. A compound card duplicating two separately clearer cards counts as one duplicate card, not two. All overlapping cards remain in the output and their errors are discussed. This avoids either counting repeated output as newly found work or choosing a favourable response to inflate response quality.

Of the **19 primary cards**, **16 select specific relevant author passages**, **2 select insufficient/unrelated passages**, and **1 correctly leaves the optional request unanswered**. The 16 relevant cards cover 15 labelled actions because the geometry action has two fragments; relevant conversation still does not prove a fix or maintainer acceptance.

| PR | Labelled actions | Full / partial / missed | Primary cards | Duplicate extras | Non-request extras | Total cards | Relevant / insufficient / correctly absent primary reply cards |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| Eventyay #6581 | 7 | 7 / 0 / 0 | 7 | 1 | 1 | 9 | 5 / 2 / 0 |
| Search-a-licious #482 | 1 | 1 / 0 / 0 | 1 | 0 | 0 | 1 | 0 / 0 / 1 |
| WPFAevent #365 | 0 | 0 / 0 / 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 |
| TeamShifts #229 | 1 | 1 / 0 / 0 | 1 | 0 | 0 | 1 | 1 / 0 / 0 |
| Exhibition #316 | 7 | 6 / 1 / 0 | 8 | 3 | 3 | 14 | 8 / 0 / 0 |
| Open Food Facts Python #527 | 0 | 0 / 0 / 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 |
| Apollo3 #867 | 2 | 2 / 0 / 0 | 2 | 0 | 1 | 3 | 2 / 0 / 0 |
| JSON Schema Test Suite #1234 | 0 | 0 / 0 / 0 | 0 | 0 | 3 | 3 | 0 / 0 / 0 |
| **Total** | **18** | **17 / 1 / 0** | **19** | **4** | **8** | **31** | **16 / 2 / 1** |

All **8 attempts completed**, and all **31 cards passed mechanical validation**. This is a particularly clear counterexample to treating exact source validity as semantic correctness. Pipeline time: median **4.009 seconds**, range **0.215–23.095 seconds**, total **59.664 seconds**. These measurements exclude human reading/correction and do not prove savings. Two of the three no-request cases correctly return zero cards; the third returns three false asks.

## Exact primary mapping and errors

Indices below are zero-based positions in the preserved per-PR `*-model.json` files.

**Eventyay #6581:** primary cards **0–4, 7 and 8** represent generic fallback, alert role, readonly error detail, portable test glob, Vite root, embedded video and inline-thread follow-through. Card **5** is a generic resolve-comments wrapper, not an eighth concrete action. Card **6** combines the repeated video/thread request; it overlaps the clearer individual cards 7/8 and is one duplicate extra.

- Card 0 selects a source-bound later author passage explicitly retaining the localized generic fallback. This author source was not in the original frozen acceptable-ID list; the earlier v10 scoring addendum already recorded it as a legitimate alternative. Its technical relevance is visible in the actual quote. This report preserves that transparent source-list omission rather than rewriting labels or marking a legitimate reply wrong merely by ID.
- Card 1's **selected quote** only says the events are covered in a browser trace. It does not say that the requested alert role was added. The generated rationale refers to a different surrounding passage about alert semantics. A true-looking rationale cannot repair an insufficient selected quote.
- Card 2 selects an author passage about Node's quoted glob and lack of Windows testing for the **readonly-detail** request. This is an unrelated reply. Its rationale again quotes different surrounding content. The card is mechanically valid and semantically wrong.
- Card 3's quoted-glob reply is relevant to the portability request while explicitly noting Windows itself was not run; do not claim cross-platform execution.
- Cards 4 and 7 select specific Vite-root and embedded-video replies. Card 8 reports rechecking the inline requests; that is relevant follow-through evidence, **not verification that GitHub threads were resolved**.
- Duplicate card 6's response addresses the video portion only, despite its request quote combining video and unresolved comments. This partial response is retained as an additional output flaw; it is not counted as another successful primary match.

**Search-a-licious #482:** card **0** captures the optional missing-field guard follow-up and correctly has no later author reply. Optional work remains within the frozen protocol even though the review approves the PR.

**Exhibition #316:** primary cards **0, 2, 4, 5, 8, 9, 10 and 12** represent test organization, initial state colors, the concrete reference dropdown, original outline colors, compact dimensions, filled colors, fixed geometry and long-option clipping. Cards 8/10 are the two partial fragments of the one compact/fixed-size action. Card 2 also mentions an early reference pattern; the clearer later reference card 4 remains the primary representation of that action.

- Duplicate **1** splits the conditional alternative from the same test-organization question; it has a null reply despite the later author explanation. Duplicates **3** and **6** restate the UI rejection/geometry complaint rather than introducing new actions beyond the concrete remedies.
- Non-request extras **7**, **11** and **13** are a bare introduction, an attachment URL and vague reaction text. None expresses a standalone concrete action. The image URL is shown as a quote, not followed or executed, but it is still a poor task card.
- Primary response spans address the specific test movement, colors, reference control and geometry changes. Card 12 contains a relevant diagnosis of browser/OS-dependent native option-popup sizing. It is a **partial investigation and tradeoff discussion**, not a finished clipping fix, exactly as the frozen labels require.

**Apollo3 #867:** primary **0** requests the existing feature-classification utility, and primary **2** requests before/after captures. Both choose specific author passages. Extra **1** is the orphan word left by splitting an abbreviation and its following noun into separate passages. That fragment is not an independently actionable request.

**JSON Schema Test Suite #1234:** all three cards quote the maintainer's reports of actions **they already completed**—dropping tests, reordering cases and adding boundary cases. They are not requests to the author. Null replies do not make these valid outstanding tasks. This important false-ask failure remains despite the focused extraction change.

**WPFAevent #365 and Open Food Facts Python #527:** no cards are emitted, correctly under the frozen labels. The Python comment's supportive suggestion remains an acknowledged alternative reading; the protocol labels it as support for the already-proposed change, not additional requested work.

## Provenance and release implication

Candidate `human-review-passages-v14`, implementation hash `5f4eae1bdf0cc265d2ee16e71e3369c39f9f178cc31e7ac6457656ea7d05d2b1`; original v10 labels hash `eee87456650129d8f751287efdfdff7a2b0f4a3e315f4e7986394e55ace674b4`; frozen manifest hash `1d50ab779fd5ce93d8e0dae1df9b1eb625fcc6ba971b3b261c80d2776072689e`; completed broad-run manifest hash `650c73a3f1e977a2462fb80e1a6442d79c5e7e41870fc5955a2a42793b72205f`.

Full inputs and first predictions remain ignored in `outputs/upgrade/evaluation/` and `outputs/upgrade/v14-broad-regression/`. The unchanged runtime/model checksums and generation settings are recorded in that run manifest. The scorer did not implement v14 and made no calls or label amendments.

This larger exposed check prevents the six-case reserved success from being presented as perfect behavior. Focused extraction repairs known omissions but can increase duplicate/context noise and still pair the wrong reply. Labels are assistant annotations from one author's convenience sample, not independent human ground truth or a real-user trial. Report the 31-card output, 12 extras, fragmented geometry ask and two primary reply errors beside the reserved and smaller regression results. ReviewRadar remains a source-linked aid requiring source inspection and human decisions; no exhaustive-task, verified-fix, time-saving or winning-probability claim is justified.
