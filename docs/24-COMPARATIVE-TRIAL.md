# Does ReviewRadar reduce the effort of resuming a review?

This is a proposed comparison protocol, not participant feedback or a time-saving claim. The existing first-use form is a usability exercise; it does not measure comparative savings.

## Recruit and prepare

Ask an actual OSS contributor who has not already studied the chosen conversations. Use two public authored PR discussions of similar length and difficulty, captured at the same time. Obtain permission before quoting feedback. Never use private PRs, credentials or identifying personal information. Keep all failures and incomplete attempts.

A person other than the implementation author should write the expected requests and relevant later replies before the trial. Label uncertain cases and disagreements rather than forcing an answer. Freeze both captures and the expected answers. The direct-reading condition must see the same captured evidence; live GitHub may have changed and is not a fair comparison without checking dates.

## Task

For each discussion, identify the concrete reviewer requests, relevant later replies, and one next action requiring inspection. Explain why a reply does or does not address the request. Export or write a short source-linked note. A completed task does not mean the PR was fixed.

Split participants between these orders:

- Participant group A: discussion 1 with direct source reading, then discussion 2 with ReviewRadar.
- Participant group B: discussion 1 with ReviewRadar, then discussion 2 with direct source reading.

Do not make one person repeat the same discussion in both conditions and then call the second run faster: familiarity would contaminate it. With only one participant, report it as a case study, not general proof.

## Record

| Field | Direct reading | ReviewRadar |
|---|---|---|
| Discussion/capture identity | | |
| Prior familiarity | | |
| Setup/preparation time | | |
| Start/end and interruptions | | |
| Reading and correction time | | |
| Correct requests / expected requests | | |
| Missed requests and extra false tasks | | |
| Relevant / incorrect reply associations | | |
| Assistance required | | |
| Useful next action with source | | |
| Would use again, and why | | |

Include installation time separately and in the first-use total. Do not compare only generation latency to human reading time. The participant should include time spent opening original sources, checking and correcting the model, saving and exporting. Ask what they would remove from the product.

## Interpretation and sharing

Publish actual counts and individual observations before averages. Do not claim net benefit if faster completion sacrifices request coverage or correctness. Retain negative feedback and incomplete trials. An agent can test the form but cannot stand in for the contributor. The participant may download notes and voluntarily share them in the existing GitHub feedback thread; this protocol does not upload answers.
