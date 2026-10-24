# Current release: source inspection and retained model failures — 25 October 2026

**ReviewRadar is a source-linked reading aid, not an exhaustive task list.** The shipped inference path remains v13. Both v14 and v15 are archived experiments, not promoted defaults. No further semantic tuning is part of this release.

| Evidence | Actual result |
|---|---|
| [v14, exposed cases containing the original three misses](v14-development/REPORT.md) | All eight labelled actions covered, previously five. Two duplicates and one insufficient reply remain. |
| [v14, separately frozen six-PR set](v14-unseen/REPORT.md) | All six labelled actions covered; two duplicate cards; four relevant reply cards and one correct null. Assistant annotations, not independent human truth. |
| [v14, broader exposed eight-PR set](v14-development/BROAD-REGRESSION.md) | 17 of 18 actions fully expressed, one fragmented. 31 cards include four duplicates and eight non-request/context extras; two primary replies wrong/insufficient. |
| [v15, broader development](v15-development/BROAD-REGRESSION.md) | Verification removes one image-URL card only; other errors remain, with extra processing. |
| [v15, separate first-attempt set](v15-unseen/REPORT.md) | Three of eight actions covered, five missed and one false request. Rejected. |
| [Restored v14 on that now-exposed set](v14-development/RETURN-REGRESSION.md) | Three of eight actions covered, five missed, two false cards. No claim that rollback solves these sources. |

The per-comment change recovers specific known omissions but can increase noise and still miss other requests. The new **Reviewer comments without a request card** panel exposes structurally unrepresented captured reviewer sources. It includes approvals/context, does not classify them as tasks, and cannot detect a missed ask inside a source that already has a card. Source reading and human decisions remain necessary.

The archived v14/v15 candidates added a 12-comment cap, 40-request cap and shared cooperative timeout; those candidate-specific controls are not claimed for v13. The shipped path retains its own source and token-budget validation. Invalid/oversize/failing input stays visibly incomplete. The old v9/v13 replay examples retain their original outputs and versions; their mistakes are not rewritten after a new model run. No genuine participant trial or measured human savings is claimed.


## Final live check: failed request-card smoke

After explicitly restoring v13 byte-for-byte (SHA-256 `24caf2b5b4713df24641ebf6c6b66b846e28893bf5aa5900ad66580530bcba47`) and restarting the app, an actual fresh Eventyay #6104 import produced analysis `87965310184944f4b82cf89c675e5401` at `2026-10-24T19:45:08.515464Z`, with prompt version `human-review-passages-v13` and **zero request cards**. Its retained sources include the review requesting screenshots/video. The smoke assertion requiring a card failed. The preceding v14 live attempt also returned zero cards. These results are not substituted with the earlier successful v13 run or excluded because the API returned structurally valid output.

Raw analyses and snapshots are retained privately under ignored `outputs/upgrade/`. This is a current integration/semantic failure, not a fresh benchmark score. The source-inspection panel gives access to unrepresented comments; it does not make the model complete or turn this check into a pass.

---

# Current evaluation — 24 October 2026

**Experimental reading aid: model cards are not a complete list of outstanding work.** Mechanical source checks do not establish conversational relevance or code correctness.

| Evidence | Observed result |
|---|---|
| [v10 fresh, eight PRs](v10-fresh/REPORT.md) | 18 assistant labels: 16 full, one partial, one missed; four duplicate and five non-ask extras; one wrong response. |
| [v11 exposed regression](v11-development/REPORT.md) | Test-location response improved; false tasks remain. Not fresh accuracy evidence. |
| [v11 separate six PRs](v11-unseen/REPORT.md) | Five asks found plus three false approval/thanks cards; one acknowledgement-only response. |
| [v12 rejected experiment](v12-development/REPORT.md) | Nine full, one partial, eight missed. Fewer cards concealed substantial recall loss; rejected. |
| [v13 frozen final, six further PRs](v13-final/REPORT.md) | Eight labels: five covered, three missed; five cards include one duplicate; one insufficient generic-test reply. Two bot-invocation cases correctly produced zero cards. |

Labels are assistant engineering annotations, not independent human truth. Fixed-order whole-PR selection, frozen hashes and first attempts are retained. Sets differ in difficulty: no combined accuracy or percentage improvement is inferred. The frozen v13 implementation was preserved; later v14/v15 experiments are reported separately and rejected as release defaults. Its narrow acknowledgement guard and local eligibility enforcement are bounded safeguards, not general intent classification.

The mixed replay preserves a separate actual v13 run on a human-only Visdom #1919 excerpt, visibly incomplete, with its missed branch-update ask and poor response retained. It is an exposed demonstration. Original v9 sample unchanged. No genuine trial or measured human savings. See [execution](../docs/19-UPGRADE-EXECUTION.md).

---

# ReviewRadar engineering pilot

23 October 2026. **This is a small engineering study, not customer validation or a population accuracy benchmark.** Labels were created by an assistant, not an independent human panel. Full case-level summaries and frozen hashes are in `results-summary.json` and `dataset-manifest.json`.

## What was tested

Four public PRs authored by the project owner supplied 53 original sources: issue comments, submitted reviews and inline comments. Seven request opportunities were annotated. Whole PRs were assigned to development (Eventyay #6104, Visdom #1872; four labels) or holdout (Visdom #1864, VoxBento #718; three labels). The examples were captured on the stated fetch date; no earlier thread or review state was invented. The initial Eventyay proof was already inspected and therefore never called holdout.

All bot sources remain in the full snapshots but are excluded explicitly from the `human_review` model and baseline queues. Empty reviews preserve GitHub state. This means source counts, human input counts and extracted request counts measure different things.

## Findings, including failures

| Run | Expected requests | Model cards | Labelled requests covered | Additional material |
|---|---:|---:|---:|---|
| Development v8 | 4 | 4 | 4 | None in the inspected development cases |
| Untouched holdout v8 | 3 | 4 | 3 | One quoted repetition was incorrectly emitted as a distinct request |
| Development regression v9 | 4 | 4 | 4 | None in these cases |
| Previously seen holdout, regression v9 | 3 | 4 | 3 | Quoted-only passages cannot be selected; a separate agreement/observation is still emitted as an additional ask |

The v8 holdout was frozen before prediction. The later quote-handling change was informed by its failure. **The v9 regression is not a new holdout**, and is not described as one. The extra agreement in the regression can reasonably be read as reinforcing the same tooling concern, but it is not a distinct pre-labelled request. It remains an extraction/duplication limitation rather than being silently relabelled to improve the score.

The expected later response source was found for each labelled request. In one case the model selected a different relevant sentence within the correct author reply; source/relationship review accepted that as the same conversational response. All displayed quotations passed source-ID, exact-text, same-PR, actor and strictly-later validation. These mechanical constraints do not establish semantic correctness, maintainer satisfaction or code correctness.

The no-model comparison queue contained five human reviewer comments on each split. It does not classify asks or pair responses. ReviewRadar's request and response selection can reduce scanning within a comment, but this study does not demonstrate a human effort reduction, and the corpus is too small to establish demand or general reliability. A single combined “accuracy” number would obscure the duplicate and small denominator.

## Development problems that changed the implementation

The first whole-PR prompt emitted author reports, approval text and an empty review as requests. A later strict-output run failed because the model omitted required fields and changed punctuation. A passage-key protocol eliminated model-written quotation text. Separating extraction and response matching prevented the model from enumerating every possible reply as a new request. Per-request response schemas then restricted choices to existing, strictly later author passages. A short referential question stays attached to its preceding issue as one exact contiguous passage. Finally, quoted-only Markdown context was excluded as a new request source, while remaining visible in Sources.

Failed iterations remain in ignored local development outputs; their results were not substituted into the final saved sample. Unknown IDs, missing request slots, malformed/truncated output and context overflow fail the affected PR visibly. There is no silent baseline substitution.

## Runtime observations

On the tested Apple Silicon Mac with 24 GiB RAM, the final v9 development PRs took 3.587 and 9.133 seconds end to end. The v9 regression PRs took 11.694 and 3.075 seconds. These are individual warm/local observations, not percentile latency or a hardware guarantee. The public sample's actual API run took 8.643 seconds for two curated PR selections; its six sources are deliberately incomplete. The run manifest records the exact model, prompt version, source identity and software hash.

## Reproduction and evidence limits

`run.py` verifies frozen source and label hashes before running. Full downloaded discussion histories and raw predictions remain local in ignored outputs to avoid redistributing long automated guides and unnecessary discussion text. Public manifests retain source URLs, IDs and hashes. A fresh GitHub fetch may have different states, edits and timestamps; it is a new snapshot and cannot be presented as the identical frozen run. These release artifacts support an inspectable pilot, not a universally reproducible benchmark claim.

No genuine participant trial, manual-reading timing, screen-reader evaluation or measured time-saving percentage has been obtained. The initial rendered audit exposed focus defects that received regression fixes. A later bounded corrected-build browser pass checked desktop/320px evidence, history/fallback focus, actual service recovery, import/inference and export; see `docs/18-FINAL-BROWSER-AND-LIFECYCLE-AUDIT.md`. Full screen-reader and actual reduced-motion preference testing remain unverified. These observations are interface evidence, not human-productivity evidence.

## Follow-up engineering change

Protocol v10 tightens eligibility for request and response text taken from explicitly marked Markdown blockquote lines, including sentence/length splits, and improves controlled external-data failure handling. The v8/v9 evaluation observations above remain version-specific historical results. A fresh v10 API smoke run completed public GitHub intake, one model evidence pair, persistence/reopen and export in 4.281 seconds for the model stage on the named machine. This is integration evidence, not a new held-out benchmark or a measured human saving.
