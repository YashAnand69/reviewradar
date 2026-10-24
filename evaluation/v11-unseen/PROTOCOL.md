# Reserved unseen whole-PR set for the next candidate

Declared 24 October 2026 before fetching these discussion bodies or running predictions. This is a new reserved engineering evaluation set, not a human trial or independent human ground truth.

## Fixed selection and contamination boundary

Continue the original frozen authored-PR search list in `outputs/upgrade/evaluation/search-selection.json` at rank18 (zero-based), immediately after the last v10-fresh selection at rank17. The original list contains80 results sorted by most recently updated descending. Screen in that order until six complete snapshots have at least one nonempty non-bot reviewer source. Exclude self-owned repositories, the original four ReviewRadar cases, all eight v10-fresh cases and any other known previously evaluated/showcased PR. Log every screened case and failure. No semantic category or organization quota; no selection based on prediction quality. Inference failures/over-budget cases must be retained rather than replaced.

Fresh means no model evaluation output inspected for these whole PRs. The author and historical OSS contribution agents may have seen the underlying discussion before. The v11 developer receives no content/labels from this reserved set before the candidate is frozen; if that separation is breached, report contamination and do not call this untouched. No model generation is allowed during preparation.

## Annotation and freeze

Read complete eligible human sources. Assistant-created engineering annotations identify concrete new asks or specific defect reports; approvals, context, completed maintainer actions and generic agreement are not tasks. Preserve optionality, repeated requests and grouping ambiguity. Record source IDs and legitimate strictly later author response IDs, including relevant investigation/clarification rather than only claims of completed fixes. If no relevant author response is visible, label null. Keep raw histories ignored; release minimal paraphrases, source IDs, provenance, exact capture dates and hashes.

Freeze protocol, snapshots and labels before the first prediction. Root reviews the Stage1 gate and records the candidate implementation/prompt hashes before permitting a run. Original labels remain byte-identical; legitimate scoring amendments are separate, explicit addenda. Do not disclose these held-out bodies or labels to the model-development worker before freeze.

## Run and score

Run each frozen case once with the frozen candidate against the local open model. No retries/best-of selection. Preserve failures, rejected input, all model artifacts and actual elapsed time. Compare the chronology baseline on identical inputs as a reading list, not a request classifier. Semantic scoring reports full/partial/missed labelled asks, duplicate/non-request extras, correct/wrong/absent response selection, ambiguity, source binding, completeness and latency with denominators. Match meaning, not only exact-ID membership. A response is conversational evidence, never code correctness or reviewer satisfaction.

Count each labelled distinct ask once. Closely coupled geometry/acceptance criteria can be grouped as one ask, with partial extraction reported explicitly; repeated reviewers do not create new distinct work. Keep subjective grouping sensitivities visible. No combined accuracy, proven time savings or population claim. A second engineering reviewer inspects substantive errors and the score. After predictions this set is exposed; later changes only yield regression evidence here.
