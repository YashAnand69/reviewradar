# ReviewRadar: Week 3 submission strategy

Verified 23 October 2026 against the current official pages. Recheck before publishing. Requirements below are separate from our design and editorial choices; no award or numerical winning probability is promised.

## Official requirements and submission gate

The [Week 3 rules](https://dev.to/page/hacktoberfest-week3-2026-10-19-contest-rules) require one new project made during 19 October, 9 a.m. PDT–25 October, 11:59 p.m. PDT; a published template-based DEV post with `hf26challenge`; open-source AI central to a Slow and Steady task; an open-innovation explanation; demo link or video; and code access. Only the first entry is considered if multiple entries are submitted. Partner entries must meaningfully use the named technology. Writing receives the most weight, followed by the listed relevance, creativity, technical execution and applicable partner criteria. These are not published numerical weights. One entrant can win one prize.

The [challenge page](https://dev.to/challenges/hacktoberfest-week3-2026-10-19) adds `devchallenge` through its template, permits AI assistance, asks for attribution of substantial prior work, and says post-deadline repository commits must be identified in the README. Its optional process/session and payoff sections are useful only when accurate.

The [general rules](https://dev.to/page/official-hackathon-rules) require eligibility, entry/material rights and acceptance by the entrant; they include promotional reuse rights and other terms. Before clicking Publish, present the finished draft and request the user's confirmation of Week 3 eligibility, rights and agreement. Week 1/2 confirmations are not substituted. Do not accept a model/provider license or legal agreement on the user's behalf. The work can be completed and the draft prepared before this final gate.

**Deadline conversion:** 25 October 23:59 PDT is 26 October 06:59 UTC and **26 October 12:29 p.m. Asia/Kolkata**. Internal target: publish 25 October IST, not at the final minute.

## Position and honest novelty

Working position: **“Read the request once. Keep the evidence beside it.”** ReviewRadar reduces the repeated effort of reconstructing what was asked and which later author response might address it across selected authored public PRs. V1 is explicitly a human-review queue: both analysis methods exclude bots from request extraction, preserve their text in Sources, and show the automated-source count. Never describe it as covering every automated finding. The product's job ends at a prepared inspection queue. People still determine whether work is actually correct and whether to reply.

This is not the first PR inbox or local AI queue:

| Existing work | Verified stated capability | Implication for ReviewRadar |
| --- | --- | --- |
| [Graphite PR Inbox](https://graphite.com/docs/use-pr-inbox) | PR-level organization including returned, waiting, approved and review states | “Which PR needs attention?” is insufficient differentiation. Compare against real status/chronology, not an empty spreadsheet |
| [GitLens Launchpad](https://help.gitkraken.com/gitlens/gl-launchpad/) | PR grouping, follow-up, snoozing, opening and action workflows | A dashboard or snooze is not novel. Keep the scope at request-level evidence and actual response association |
| [Slow Triage Week 3 entry](https://dev.to/stefan_juang/slow-triage-a-local-first-issue-review-queue-that-knows-when-to-wait-36lg) | Local synthetic issue classification/duplicate suggestions, reversible queue, abstention and comparison with a baseline | Citations, local processing and uncertainty alone do not establish distinctiveness. Use real PR histories and demonstrate the request/response task. Its published limitations are that author's reports, not our independent benchmark |

The proposed distinction is a hypothesis to demonstrate, not a claim of global originality: an authored-PR request clause paired with possible later response evidence, explicit GitHub/local/model state separation, and real-history evaluation. Credit research inspiration where appropriate; do not copy another entry's prose, code or branding.

## Evidence required for each judging dimension

| Dimension | Submission evidence | Avoid |
| --- | --- | --- |
| Writing | One concrete opening case, short before/after workflow, readable screenshots, direct demo/code links, actual results plus one failure | Inflated adjectives, a long feature inventory, unexplained test counts |
| Theme | Show repeated rereading replaced by a prepared queue; preserve the person's slower deliberate final decision | Claiming that more notifications or auto-commenting is laziness saved |
| Creativity | Explain the request-level distinction and compare a stale request with a later relevant response | Claiming the first PR assistant, first local triage or first uncertainty UI |
| Technical execution | Actual public intake, local model invocation, deterministic source checks, persistence/export, recoverable failures, independent tests | Passing screenshots as proof, valid citations as proof of correct interpretation, a static sample described as live |
| Gemma | Pinned model identity, verified local run, example input/output, task-level comparison and meaningful contribution to extraction/association | Merely mentioning an installed model, decorative provider branding or a fallback result called model output |

## Article structure

Use the official [submission template](https://dev.to/challenges/hacktoberfest-week3-2026-10-19) and preserve its required information:

1. **What I Built:** lead with one genuine source-backed review scenario. State the intended user, chore, boundaries and what the person still does.
2. **Demo:** put public sample and short actual-local-run video early. Label the former historical replay before the link. Explain that online GitHub intake needs internet; inference can run locally after installation/import.
3. **Code:** fresh ReviewRadar repository, license, setup/run instructions and fixed release commit. Do not link the Week 2 app as this project's source.
4. **How I Built It:** clear intake → immutable snapshot → baseline/model interpretation → validated sources → human inspection → local decision path. Explain one substantive failure found and fixed. Link exact evidence/results; report unresolved limits. Eventyay #6104 is development-only because its output has already been inspected; disclose and correct the failed initial model proof rather than presenting it as held-out success.
5. **Why Does Open Innovation Matter?:** practical local control and swappable model/runtime. No closed inference API dependency or per-request API fee for this configuration. Downloads, internet for fresh intake, hardware, electricity and installation still cost time/resources; “free” does not imply zero setup.
6. **My Agent Session (optional):** link only if an actual captured shareable session exists and is safe to disclose. Otherwise omit; never manufacture one.
7. **The Lazy Payoff (optional):** include measured human results only after an actual trial, with participant count, method, correction time and limits. If absent, omit the numerical-payoff section and state that usability/engineering evidence is not measured human savings.
8. **Prize Categories:** Overall consideration plus **Best Use of Gemma** only if meaningful Gemma processing is working and evidenced. Do not add unimplemented partner integrations.
9. **Credits and AI assistance:** accurately identify the user's actual choices/testing and AI-assisted design/implementation/writing. Do not imply human-only authorship. Public discussion authors retain their material rights; source attribution does not automatically transfer those rights.

The article should be specific and understandable without knowing this conversation. Use synthetic adversarial cases only where explicitly labelled, and distinguish them from real historical public PR examples. Avoid repeating long third-party comments in the public write-up; small attributed excerpts and original-source links usually tell the story better.

## Demo storyboard

A focused 90–150-second recording target, with real elapsed model time shown or a clearly announced cut:

1. A real source discussion and the small question the user would have to reconstruct.
2. Import a selected public snapshot or execute public GitHub intake. Display fetch date, completeness and PR scope.
3. Run the local model; show actual model identity and wait/error state rather than a fake progress percentage.
4. Inspect one request/response pair and one unresolved/unclear case. Open its validated original source. Show GitHub state separately.
5. Mark a local decision, undo it and export the prepared work list. Explain that GitHub was not changed.
6. Show the public replay label, setup/source link and the main limitation. A recording of the actual app is different from a reconstructed animation; identify any edits accurately.

## Final publication checklist

- Public source and demo are reachable logged out; no secrets, credentials, private text, model weights or unrelated project files in release.
- Entry title, cover and screenshots correspond to the release, with historical/sample labels readable.
- The article reports actual model, hardware/runtime, evaluation sizes and results. No cherry-picked percentage without denominator, no test-count-to-accuracy substitution.
- AI assistance and third-party source/license credits are accurate. No manufactured testimonial, fabricated trial, reaction manipulation or repeated unsolicited maintainer pings.
- Required tags present; meaningful categories listed. Exactly one Week 3 submission is published and its URL recorded.
- User's final Week 3 eligibility/rights/agreement confirmation recorded, then publish and verify the public result.
- Freeze the submitted release commit and record time. Label material post-deadline changes in README and avoid suggesting they were part of the judged snapshot.
