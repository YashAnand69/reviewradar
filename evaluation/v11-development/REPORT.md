# v11: exposed development regression

Run on 24 October 2026, 16:39–16:40 UTC. This is **development/regression evidence**, not unseen performance: the candidate was informed by errors on these same eight v10-fresh PRs. The assistant scorer inspected the preserved actual cards against the original frozen labels; no labels or predictions were overwritten. This is engineering annotation, not independent human ground truth or demonstrated time savings.

## Counts

Against 18 labelled asks, the 22 emitted cards contain **16 fully covered asks, 1 partially covered ask, 1 missed ask, 1 duplicate extra and 4 non-request extras**. Of 17 matched ask cards, 16 select relevant later author passages and 1 correctly has no response; no clearly wrong primary response association remains on this exposed set. “Relevant” includes investigation/clarification and does not mean a verified completed fix.

| PR | Labels | Full / partial / missed | Cards | Duplicate / non-request extra |
| --- | ---: | --- | ---: | --- |
| Eventyay #6581 | 7 | 7 /0 /0 | 8 | 1 /0 |
| Search-a-licious #482 | 1 | 1 /0 /0 | 1 | 0 /0 |
| WPFAevent #365 | 0 | 0 /0 /0 | 1 | 0 /1 |
| Teamshifts #229 | 1 | 1 /0 /0 | 1 | 0 /0 |
| Exhibition #316 | 7 | 5 /1 /1 | 7 | 0 /1 |
| OFF Python #527 | 0 | 0 /0 /0 | 1 | 0 /1 |
| Apollo3 #867 | 2 | 2 /0 /0 | 2 | 0 /0 |
| JSON Schema #1234 | 0 | 0 /0 /0 | 1 | 0 /1 |
| **Total** | **18** | **16 /1 /1** | **22** | **1 /4** |

All 8 attempts completed and all 22 cards passed mechanical source-bound validation. The chronology baseline contains 21 human-reviewer comments and is not a request classifier. Observed model wall time: median 3.793 s, range 2.704–21.914 s, total 59.915 s; this excludes installation, reading and correction.

## Case-level findings

- Exhibition's test-organization response now correctly selects the earlier author paragraph moving UI assertions into existing suites. The v10 wrong association to a later colour/size update is absent in this run.
- Eventyay still repeats the embedded-video ask across two reviewers: card 6 duplicates card 5. Its other seven distinct asks are represented. The generic-fallback reply is a legitimate later source omitted from the original acceptable-ID list; retain the transparent addendum in the v10 report rather than rewriting frozen labels.
- Exhibition card 3 is a bare introductory imperative without its concrete requirements; count it as a non-request extra. Card5 covers fixed size but omits compact width/height, so the coupled geometry label is partial. The explicit original-outline-colour refinement remains missed. This grouping is a documented judgement call, not an objective universal boundary.
- WPFAevent's workflow-approval waiting statement becomes a false new task, although the PR contains approval rather than a concrete author request.
- OFF Python's supportive context becomes a new request. Its optional-suggestion counter-reading remains documented in frozen labels; the declared concrete-new-ask interpretation is retained.
- JSON Schema's maintainer report of tests they already added still becomes one new ask. It produces fewer false cards than v10, but the semantic defect is not eliminated.
- Thread-resolution and clipping responses remain reports/clarification, not proof of completion. The generic-fallback quote remains awkwardly partitioned inside a translated error sentence.

## Comparison and identity

The original v10 scoring was rechecked against its preserved cards:16 full, 1 partial, 1 miss, 4 duplicates, 5 non-request extras and 1 wrong primary response match remains consistent under its declared grouping. This recheck does not constitute a new independent human review; the same engineering annotator prepared the original labels/score. v11 reduces some exposed-set clutter and fixes the observed test-response pairing, while preserving a miss and adding a workflow-wait false task. Do not call the difference a holdout improvement percentage.

The candidate is `human-review-passages-v11`, implementation SHA-256 `26a0beeb956ac0efefe1935319e3e5c79438b57a0766e04afe88bc3810911ab8`, prompt SHA-256 `139b592743f0bceef78d36c09955e65d0f6c0bca08fae66c81a95e15eafab1b1`. Input/label identity is [the v10-fresh freeze](../v10-fresh/freeze-manifest.json), labels hash `eee87456650129d8f751287efdfdff7a2b0f4a3e315f4e7986394e55ace674b4`.

Actual first-attempt artifacts and timing are preserved locally at ignored `outputs/upgrade/v11-development/`. Settings: local Gemma 4 E2B Q4_0, 16,384 context, 2,048 output, 1,024 margin, temperature 0, no retry/best-of. Full model/runtime hashes are in the preserved run manifest. Review all numerical claims alongside the [v11 unseen report](../v11-unseen/REPORT.md); this development set alone cannot justify release quality.
