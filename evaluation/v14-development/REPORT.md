# v14 focused extraction: exposed regression evidence

The v14 candidate was frozen on 24 October 2026 at 19:16:57 UTC, before this run. It extracts separately from each eligible reviewer comment while retaining the full reviewer context, constraining selectable keys to the focus comment and carrying prior selections forward. The frozen six-case v13 evaluation is already exposed development evidence. This rerun does **not** become an untouched test by changing the prompt version. All original v13 sources, labels and outputs remain unchanged.

## Independent engineering score

All **8 labelled requested actions are fully covered**, with **0 partial and 0 missed**. The run emits **9 cards**: **7 matched ask cards** cover those 8 actions because one compound card covers two independently labelled changes, and **2 additional cards repeat the rationale for represented requests**. There are **0 unrelated/non-request extras beyond those rationale duplicates**.

Of the **7 matched ask cards**, **5 select specific relevant later author passages** (covering 6 requested actions), **1 selects an insufficient/unrelated test-pass passage**, and **1 correctly leaves the response absent** for the template request with no visible later author response. Relevant response text is not proof of code correctness or completion.

| PR | Labelled actions | Full / partial / missed | Cards | Rationale duplicates | Relevant / insufficient / correctly absent matched response cards |
| --- | ---: | --- | ---: | ---: | --- |
| Open Prices Frontend #2472 | 0 | 0 / 0 / 0 | 0 | 0 | 0 / 0 / 0 |
| Visdom #1919 | 2 | 2 / 0 / 0 | 3 | 1 | 1 / 1 / 0 |
| Visdom #1952 | 0 | 0 / 0 / 0 | 0 | 0 | 0 / 0 / 0 |
| Visdom #1929 | 2 | 2 / 0 / 0 | 1 | 0 | 1 / 0 / 0 |
| Visdom #1954 | 2 | 2 / 0 / 0 | 3 | 1 | 2 / 0 / 0 |
| Visdom #1928 | 2 | 2 / 0 / 0 | 2 | 0 | 1 / 0 / 1 |
| **Total** | **8** | **8 / 0 / 0** | **9** | **2** | **5 / 1 / 1** |

All six first attempts completed and all nine cards passed mechanical source-bound validation. Chronology contains nine reviewer comments; it is a reading list, not a semantic classifier. Nine generated cards do not demonstrate queue compression. Pipeline wall times: median **4.812 seconds**, range **0.209–6.840 seconds**, sum **23.973 seconds**. These include eligibility and runtime work, not human reading or installation, and are not measured savings.

## What improved, and what remains wrong

- The three v13 omissions—branch update, preservation of the caller's options object, and the PR-description template—are now represented. This is a successful regression repair on known cases, not evidence of general recall.
- The underflow warning request now selects the author paragraph explicitly reporting a warning when a finite nonzero vector becomes zero. Its old generic test-pass selection is corrected.
- The newly recovered branch-update card in Visdom #1919 selects a later inline test-pass statement rather than the earlier author paragraph reporting the branch update. The selected exact quote does not establish that the branch was updated. The source is real and later, but its semantic match is still wrong.
- Visdom #1919 also emits the explanation that data can silently become zero as another request card. That sentence is the reason for the same requested warning, not an additional task. Its selected response discussing cases that do not trigger a warning does not justify the model's claimed mitigation.
- Visdom #1954 again emits the all-NaN-warning rationale separately from the requested unused-bound reduction change. It is a duplicate rationale card, and test-pass prose must not be treated as independent verification of resolution.
- The compound Visdom #1929 card still explicitly covers both removing the unnecessary statement and preserving coverage of two rendering paths, with a response addressing both. Its two-action denominator is retained.
- Both human bot-invocation cases correctly produce no cards. This narrow result does not establish reliable handling of every kind of acknowledgement or status discussion.

## Provenance and limitations

Candidate `human-review-passages-v14`, implementation SHA-256 `5f4eae1bdf0cc265d2ee16e71e3369c39f9f178cc31e7ac6457656ea7d05d2b1`, prompt hash `174b6945d0f01c7e63228b8ff3c1c926ad7ad6843ef90097e13935ea89817301`. Frozen labels hash `5b7b4453e2ee5aa28e4c7f58dfd07c1f4a1ddcd8a2d304e8a74cac4faa67d365`; source manifest hash `6857d0466ebb3b55503763fa323deb0e8843a02f7de7404b677ccfb2f1c3ba0b`. Candidate metadata is in `candidate.json`; actual first-attempt predictions and run metadata remain in ignored `outputs/upgrade/v14-development/`.

The same Gemma 4 E2B Q4_0 artifact, runtime, 16,384-token context, 2,048-token output, 1,024-token reserve, temperature zero and 90-second cooperative whole-PR budget were used. A currently blocked network read remains bounded by its configured read timeout; cooperative chunk/deadline checks are not an OS-level hard cancellation promise.

The scorer did not implement v14 and checked actual selected spans against the frozen assistant annotations. This is independent engineering review, not independent human adjudication or a genuine user trial. Five of six cases are Visdom and all come from one author's convenience sample. No population accuracy, human time saved or winning probability follows from these results. The separate v14 reserved set must be reported independently; do not pool it with this exposed regression or select only successful examples.
