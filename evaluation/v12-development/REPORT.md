# v12: rejected exposed development candidate

Run on 24 October 2026, 16:44–16:45 UTC. **Rejected for severe recall regression.** This candidate was informed by the already exposed v10/v11 errors and ran on the same 8 v10-fresh discussions. These are development/regression results, not unseen performance. No reserved v12-unseen discussion body was read for this assessment.

## Counts

Against 18 frozen labelled asks, 12 emitted cards contain **9 fully covered asks, 1 partially covered ask, 8 missed asks, 1 duplicate extra and 1 non-request extra**. Of 10 primary matched ask cards, 9 select relevant author passages and 1 selects the wrong passage. The only expected-null ask was missed, so there is no successful null-selection denominator in this run.

| PR | Labels | Full / partial / missed | Cards | Duplicate / non-request extra |
| --- | ---: | --- | ---: | --- |
| Eventyay #6581 | 7 | 1 /0 /6 | 1 | 0 /0 |
| Search-a-licious #482 | 1 | 0 /0 /1 | 0 | 0 /0 |
| WPFAevent #365 | 0 | 0 /0 /0 | 0 | 0 /0 |
| Teamshifts #229 | 1 | 1 /0 /0 | 1 | 0 /0 |
| Exhibition #316 | 7 | 5 /1 /1 | 8 | 1 /1 |
| OFF Python #527 | 0 | 0 /0 /0 | 0 | 0 /0 |
| Apollo3 #867 | 2 | 2 /0 /0 | 2 | 0 /0 |
| JSON Schema #1234 | 0 | 0 /0 /0 | 0 | 0 /0 |
| **Total** | **18** | **9 /1 /8** | **12** | **1 /1** |

All 8 attempts completed and all 12 cards passed mechanical source-bound validation. The chronology baseline still contains 21 reviewer comments. Wall time median 1.254 s, range 0.268–19.020 s, total 31.526 s. Lower time and fewer cards are not improvements when legitimate asks disappear.

## Why this cannot ship as a repair

- Eventyay #6581 previously yielded the five concrete technical requests plus the video and thread-follow-through requests. v12 emits only the generic-error fallback request, missing six labelled asks. This is a major core-task regression, even though coverage is mechanically marked complete.
- Search-a-licious's optional missing-field guard ask disappears. The frozen annotation explicitly preserves this as an optional concrete follow-up, not an approval-only source.
- Pure approvals/context and completed maintainer-action false cards disappear on WPFAevent, OFFPython and JSONSchema, but that gain is outweighed by lost real asks. Do not report only the cleaned-up false positives.
- Exhibition retains a bare introductory imperative as an extra, misses the explicit outline-colour refinement and only partially captures the coupled compact/fixed geometry ask.
- Exhibition has two overlapping dropdown-pattern cards. The explicit reuse-existing-control card selects a passage about restored outline colours, which does not explain using the existing control. The less informative general complaint card selects the correct native-control replacement passage. Under the same primary-explicit-ask grouping used for v10, count the generic complaint as a duplicate and the explicit card's response as wrong. This choice and the correct duplicate's passage are both visible; there is no claim that the entire discussion lacks a relevant author reply.
- The Eventyay generic-fallback card again selects a semantically valid later inline source omitted from the original acceptable-ID list. Preserve the original labels and v10 transparent scoring addendum.

## Identity and comparison

Candidate `human-review-passages-v12`, implementation SHA-256 `63703ac19ebe9dedf03b8ea4d9c203bcdac40e1276bfcc241c170e4fae196bad`, prompt SHA-256 `d0beb84cb02a929635b3a355a85b600a99108ce43988c65dbaa0eaece9ab09cc`. Inputs and labels are the unchanged [v10-fresh freeze](../v10-fresh/freeze-manifest.json), label hash `eee87456650129d8f751287efdfdff7a2b0f4a3e315f4e7986394e55ace674b4`. Full first-attempt artifacts remain ignored in `outputs/upgrade/v12-development/`.

Settings: Gemma 4 E2B Q4_0, 16,384 context, 2,048 output, 1,024 margin, temperature 0, no retries/best-of. The engineering scorer did not implement this candidate. Grouping/optionality sensitivity, single-author convenience sampling and assistant-only labels remain the same as the original protocol. No measured human benefit or combined accuracy is claimed.

**Decision:** retain this failed experiment as evidence and do not release v12. A later repair requires its own frozen identity; exposed-set reruns are regressions, and only still-uninspected reserved cases can provide new first-attempt evidence.
