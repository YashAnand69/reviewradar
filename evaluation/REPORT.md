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

No genuine participant trial, manual-reading timing, screen-reader evaluation or measured time-saving percentage has been obtained. Browser visual/keyboard/mobile verification is currently blocked by disabled browser access in this Work session. Those limits must stay in the release report until actual checks occur.
