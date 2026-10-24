# Restored v14 on the now-exposed v15 pool

This check uses the **exact previously frozen v14 implementation**, after v15 was rejected as an additional verification stage. The v15 pool was already predicted and scored, so this is **exposed rollback regression evidence**, not an untouched v14 test. No prompt modification, label amendment, retry or case replacement occurred. The run took place at 2026-10-24 19:36 UTC.

## Independent score

The restored v14 pipeline captures **3 of 8 labelled actions**, with **0 partial and 5 missed**, the same action coverage as v15 on these inputs. It emits **four cards**: **two matched ask cards** cover three actions, and **two false non-request cards** describe closure/comparison context. There are **zero duplicate cards**. Both matched cards correctly select no response, covering three of six expected-null actions. Both labelled actions with actual later author responses are missed, so this run provides **zero successful matching examples with a visible reply**.

| PR | Labelled actions | Full / partial / missed | Cards | Non-request extras | Correct absent-response cards |
| --- | ---: | --- | ---: | ---: | ---: |
| Panel #8810 | 0 | 0 / 0 / 0 | 0 | 0 | 0 |
| Scrum Helper #904 | 1 | 1 / 0 / 0 | 1 | 0 | 1 |
| Voxbento #717 | 1 | 0 / 0 / 1 | 0 | 0 | 0 |
| Voxbento #716 | 1 | 0 / 0 / 1 | 0 | 0 | 0 |
| Eventyay #6220 | 3 | 0 / 0 / 3 | 2 | 2 | 0 |
| Eventyay #6219 | 2 | 2 / 0 / 0 | 1 | 0 | 1 |
| **Total** | **8** | **3 / 0 / 5** | **4** | **2** | **2** |

The substantive misses remain important:

- Voxbento #716 explicitly requests checking whether the reporter intends to author a fix before taking future issues. The pipeline misses it despite a relevant later author apology and stated screening change.
- Voxbento #717 objects to a patch whose reporter had already coordinated ownership. This is an implicit rather than literal request, and its alternative non-request reading remains in the frozen labels. Excluding this one ambiguous action still leaves **3 covered and 4 missed out of 7**, rather than reliable recall.
- Eventyay #6220 contains three concrete future-process tips: a screencast, addressed automated review feedback and passing CI. All three are missed. Instead, the two cards select the maintainer's report of closing in favor of another PR and the reason that competing PR was preferred. These are completed/comparative context, not requested author actions.
- Scrum Helper #904's optional test-only follow-up and Eventyay #6219's compound screencast/CI guidance remain correctly captured with null responses. Closed PR status does not erase historical guidance or authorize reopening a rejected PR.

## Comparison and validation

v15 emits three cards on the same pool, with the same three captured actions and five misses. The difference is one additional false closure card under restored v14. The prior [broad regression](BROAD-REGRESSION.md) similarly shows only one fewer false image-URL card under v15 while retaining many semantic errors and adding runtime work. These limited differences do not justify a dependable semantic-verification claim.

Final analysis artifacts do not preserve intermediate focused extraction and verification selections. Therefore this report **does not claim where either pipeline internally lost the genuine asks**, nor that the verifier specifically caused all misses. It compares observed final outputs of frozen implementations.

All six attempts completed; the independent scorer rechecked every frozen snapshot hash and all four bound analyses/cards. All passed mechanical validation. Exact source validity therefore coexists with missing requests and false tasks. Pipeline wall time: median **1.269 seconds**, range **0.001–3.787 seconds**, sum **8.885 seconds**. v15's sum was 8.825 seconds on this pool; these are single observations, not a robust latency comparison or evidence of human savings. Do not claim a measured speed benefit from the rollback.

Frozen v14 implementation SHA-256: `5f4eae1bdf0cc265d2ee16e71e3369c39f9f178cc31e7ac6457656ea7d05d2b1`; labels SHA-256: `b65e69912cfd6c289df2fe5b97bcb96cc63cd6e607959490beddeae2fd302bb6`; frozen pool manifest: `ea3acb43b557dcb686f4df4391ab8d10b2dccfb6638832a632040dd2d3ed86eb`. Completed run-manifest SHA-256: `971e3a3a5a8078262071508a90b88c7b5f3a038b4ceb4d1d80a47f9d50a9ece3`. Full first attempts and run identity remain ignored in `outputs/upgrade/v14-return-regression/`. No additional inference or tuning was performed by the scorer.

This result must accompany the earlier 8/8 exposed repair and 6/6 reserved result. Recovering the original three missed asks does **not** mean the model is now exhaustive or perfect. ReviewRadar remains a source-linked reading aid requiring inspection of original comments, including sources with no generated card. It cannot certify completed work, maintainer satisfaction, independent user validation, measured productivity or a winning outcome. No further prompt runs are part of this release decision.
