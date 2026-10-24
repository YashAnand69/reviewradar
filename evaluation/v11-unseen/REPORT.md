# v11: first-attempt reserved engineering set

Run on 24 October 2026, 16:41 UTC. Six whole PRs and their assistant annotations were frozen before candidate predictions. This is the **first attempt on this reserved set**, with no retries. It is not an independent human trial or representative GitHub benchmark. The discussions may have been encountered by the author in earlier OSS maintenance; “unseen” refers to ReviewRadar model-evaluation output. After this run the set is exposed and cannot validate later candidates as unseen.

## Counts

The model found all 5 labelled asks, but emitted8 cards: **5 fully covered asks, 0 partial/missed asks and 3 non-request extras**. Of 5 matched ask cards,**4 select technically relevant author passages;1 selects an insufficient acknowledgement rather than the available technical response**. There are no expected-null asks in this pool, so it supplies no no-response matching denominator.

| PR | Labelled asks | Model cards | Non-request extras | Relevant / insufficient primary replies |
| --- | ---: | ---: | ---: | --- |
| Eventyay Socialmedia #84 | 0 | 2 | 2 | 0 /0 |
| Visdom #1924 | 2 | 2 | 0 | 2 /0 |
| Visdom #1923 | 1 | 1 | 0 | 0 /1 |
| Apollo3 #864 | 1 | 1 | 0 | 1 /0 |
| Apollo3 #861 | 0 | 1 | 1 | 0 /0 |
| Open Prices Frontend #2471 | 1 | 1 | 0 | 1 /0 |
| **Total** | **5** | **8** | **3** | **4 /1** |

All 6 attempts completed; all 8 emitted cards passed mechanical quote/source/chronology checks. The chronology reading list contains 9 reviewer comments. Wall time median 3.372 s, range 2.431–6.051 s, total 23.398 s, excluding setup/reading/correction. Do not convert these counts into a combined “accuracy,” proven saving, general model capability or comparison percentage with the more complicated development set.

## Errors that matter

- **Approvals become work:** the two Socialmedia approval sources become separate request cards. Apollo861's thank-you source also becomes a request. Both no-ask PRs therefore get false work cards; source validity does not prevent this semantic error. The rationales themselves recognize approval/thanks, making the erroneous task framing especially clear.
- **Acknowledgement is not a technical reply:** Visdom #1923 selects the author's sentence apologizing for missing the request. The sentence repeats the CI topic but does not report doing, explaining or investigating the requested test-dependency fix. The same full author comment contains a later concrete paragraph adding the Plotly dependency and removing silent skipping. The selected quoted passage is therefore insufficient, despite the correct comment ID and an otherwise relevant full source. Count this against response evidence; do not silently award a correct technical match because the full comment contains an answer elsewhere.
- Visdom #1924's two explicit-validation asks, Apollo864's test-location ask and the screenshot request select relevant author passages. These remain conversational claims, not independently verified changes.
- The closure/inactivity announcement on Visdom #1923 is not extracted as a separate task in this run. That isolated success does not offset the three false approval/thanks tasks.

## Scope, freeze and candidate

The fixed original search was continued at ranks18–30 until6complete human-reviewed cases were selected;7 cases lacked eligible human-reviewer text. The pool has only 5 asks, all responded to, and two simple approval/thanks cases. No semantic quota or favourable-prediction filtering was imposed. It cannot establish partial-response, large-multiask, quotation-heavy or no-response performance.

The [protocol](PROTOCOL.md), [labels](labels.json) and [freeze manifest](freeze-manifest.json) remain unchanged. Labels SHA-256 `200456403bc68661310456eeaa01c87a911a84844e48d665d6caf3290e7e5d23`; freeze SHA-256 `077ed201a0f49542785f3741805f83201df41e5ad7b0533a37486c3b2ef5ce09`.

Candidate `human-review-passages-v11`, frozen before predictions: implementation `26a0beeb956ac0efefe1935319e3e5c79438b57a0766e04afe88bc3810911ab8`; prompt `139b592743f0bceef78d36c09955e65d0f6c0bca08fae66c81a95e15eafab1b1`. Settings: Gemma 4 E2B Q4_0, 16,384 context, 2,048 output, 1,024 margin, temperature 0. Full runtime/model identity and actual results remain ignored in `outputs/upgrade/v11-unseen/first-run/`. The scorer did not implement this candidate. No original label or prediction was modified, and no v12-unseen body was read for this report.

**Decision:** this first-attempt set exposes unresolved false-task framing and weak selected-response evidence. It supports a need for repair and honest limits, not a claim that v11 solved the problem. Subsequent use of these cases is regression evidence.
