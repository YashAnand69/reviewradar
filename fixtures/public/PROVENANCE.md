# Public historical sample: provenance and limits

This is a deliberately **incomplete, curated historical sample**, captured through read-only GitHub GraphQL on the `fetched_at` date in `historical-sample.json`. It is not the user's current inbox. No selected source body is truncated or rewritten; omitted context is explicitly disclosed in the snapshot and each PR's warnings.

The fresh local intake covered 53 sources across four public PRs. Only six exact sources are included in this public sample. Bot messages, other submitted reviews, author updates, later discussion and other PRs are omitted. Source completeness is therefore false. The local source snapshot and any analysis against this excerpt have different content identities from full-history analyses; results must not be copied across those identities.

## Included sources

| PR | Source and author | Why selected |
| --- | --- | --- |
| [Eventyay #6104](https://github.com/fossasia/eventyay/pull/6104) | [17-word request, Saksham-Sirohi](https://github.com/fossasia/eventyay/pull/6104#pullrequestreview-5396298833) | A concrete screenshot/video request |
| Eventyay #6104 | [Author reply, YashAnand69](https://github.com/fossasia/eventyay/pull/6104#issuecomment-5965628217) | A later report of screenshot additions; not proof of correctness |
| [Visdom #1872](https://github.com/fossasia/visdom/pull/1872) | [Bug report, Manik-Khajuria-5](https://github.com/fossasia/visdom/pull/1872#pullrequestreview-5336051374) | A short implicit request to inspect dtype behavior |
| Visdom #1872 | [Author reply, YashAnand69](https://github.com/fossasia/visdom/pull/1872#issuecomment-5874038042) | A later report of reproduction and regression checks |
| Visdom #1872 | [Normalization request, Manik-Khajuria-5](https://github.com/fossasia/visdom/pull/1872#pullrequestreview-5349785561) | A separate request on the same PR |
| Visdom #1872 | [Author reply, YashAnand69](https://github.com/fossasia/visdom/pull/1872#issuecomment-5891608254) | A possible response distinct from the earlier dtype response |

Source IDs, actors, original dates, review states and current-at-fetch PR state/head SHA are retained. These are actual fetch metadata, not fabricated snapshots from an earlier date. Merge/closure/approval is not independent verification of a code fix. The sample shows conversation evidence only.

## Rights and attribution

Third-party discussion text remains attributable to its original authors. ReviewRadar's software license does not relicense these comments, nor claim ownership over GitHub branding or source repositories. This small attributed sample exists to explain and evaluate the review-reading task; original context remains available through the links above. Reusers should assess rights for their own redistribution rather than assume a blanket license over public comments. User-authored replies are included for this authorized project demonstration.

Full fetched source histories remain in ignored local `outputs/` for engineering evaluation and are not bundled in the public sample. Engineering labels and dataset metadata describe the limited corpus and split; they are not a participant trial, an endorsement from source authors or evidence of general model reliability.

## Mixed-evidence example — 24 October 2026

`frontend/public/mixed-sample.json` is a separate normalized snapshot and actual v13 run on [Visdom #1919](https://github.com/fossasia/visdom/pull/1919), captured 24 October. Nine exact human entries from 18 captured entries are retained, including empty reviews carrying GitHub state. Nine automated entries and long guides omitted. Snapshot/PR explicitly report incomplete intake. Source IDs, URLs, actors, original dates and exact bodies remain; no selected body rewritten.

Jayantparashar10 requested a branch update; Manik-Khajuria-5 requested an underflow warning. User-authorized YashAnand69 replies supply later context. Actual saved output misses the branch ask and selects a generic test result poorly. It is preserved as a correction exercise, not a fresh benchmark. Manifest records candidate hash, input identity and capture/analysis dates. It does not copy an analysis across snapshot identities. Rights/attribution boundaries above apply; this limited sample does not relicense third-party comments. Full raw histories remain ignored.
