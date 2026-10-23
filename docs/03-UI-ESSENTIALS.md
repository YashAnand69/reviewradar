# ReviewRadar — UI essentials and interaction specification

Version 1 · 23 October 2026 · Design specification, not a claim that checks have passed.

## 1. Design intent

A calm evidence workbench that gets the contributor to the original ask quickly. Distinctive through editorial clarity, paired passages and deliberate interaction rather than a long animated landing page. Make uncertainty easy to inspect; do not simulate certainty through colour, progress rings or a polished “done” state.

The same interface serves the local full-stack application and public sample. **Mode, capture date and coverage are persistent context**, never a dismissible toast. The hero is the working review surface, not marketing copy.

## 2. Information architecture

```
Header     ReviewRadar             Local / Replay · captured date   Help
Context    Snapshot title · N PRs · source count · completeness      New source
Controls   All requests | Follow-up | Possible response | Unclear   Reviewed toggle
Workbench  Request list (left)     Selected evidence (right)
Footer     Baseline/model · elapsed · source coverage · export
```

Desktop uses a restrained two-column workbench: a 340–390 px list and flexible evidence panel, maximum content width about 1440 px. The selected PR's metadata is close to its request, not a separate dashboard page. At narrower widths, switch to list → detail with an explicit back action that preserves selection, filters and scroll position. Do not squeeze two unreadable columns onto a phone.

Recommended small navigation: “Review” and “Sources”; “How it works” in an accessible help panel. Evaluation/installation links can live in the header/help footer rather than crowding the core task. A compact introduction on first visit offers “Explore the public sample” and “Use the local app”.

## 3. Visual system

| Token | Direction |
| --- | --- |
| Canvas | Warm off-white `#F7F7F2`; avoid dark-dashboard sameness |
| Surface | White `#FFFFFF`; selected surface pale teal `#EAF4EF` |
| Text | Near-black green `#182C29`; secondary `#526560` |
| Accent | Deep teal `#17634F`; white text on primary actions |
| Border | Soft neutral `#D8E1DC`; stronger selected border `#4D8A75` |
| Caution | Dark amber `#805A13` on pale cream `#FFF4D9`; never colour alone |
| Error | Dark red `#9A3636` with written cause and recovery action |
| Spacing | 4, 8, 12, 16, 24, 32, 48 px scale |
| Shape | 10–14 px panels; 6–8 px compact controls; avoid every label becoming a pill |
| Type | Local/system sans for controls and prose; system mono for source IDs/timestamps where useful |
| Depth | Minimal single soft shadow on floating panels; borders do most hierarchy work |

Verify contrast in rendered UI rather than treating sample hex values as a compliance claim. Body text around 15–16 px, comfortable 1.5 line height, evidence quotes 16 px, page heading 28–36 px. Avoid low-contrast uppercase microtype for important state. Do not fetch web fonts at runtime; local-first includes a predictable offline interface.

A quiet radar/paired-line motif may appear as a small native SVG mark or processing indicator. It must not imply monitoring or a real scan rate. No hero illustration is required; the strongest visual is the real evidence pair.

## 4. Source and analysis onboarding

### First visit

Show one sentence: “Find the request. Read the response. Decide what needs another look.” Subtext explains read-only public PRs and local inference. The sample button is primary because it removes installation friction. A visible “Historical sample — no live GitHub sync” label accompanies it.

### Source panel

- GitHub handle field with visible label and explanation: “Only public PRs authored by this account.”
- One URL per line; show a count and max five before submission. No vague “Connect GitHub” button if no OAuth exists.
- Explain that GitHub credentials remain with the local CLI and model processing stays local. Public demo disables live import with a clear setup link; it does not show a fake login.
- Snapshot upload has a plain file selector and format help. Do not require drag-and-drop.
- Before analysing, list source types and counts for each PR, fetch date, author and state. Highlight capped/failed streams explicitly.
- A missing model is not a broken onboarding flow: retain source reading and explicit chronology baseline, explain local setup.

### Processing

Use a static, announced label plus subtle motion: “Reading 3 selected PRs locally…”. Show elapsed seconds and the actual task stage only if the server reports it. Do not invent percentage completion, animate a fake queue of completed PRs, or state that processing continues after navigation unless it truly does. Avoid a cancel button unless cancellation actually stops or safely ignores the work and explains its semantics.

## 5. Request list

Each row/card contains:

1. Repository and PR number; optional concise title on hover/detail, not essential hover-only information.
2. A short exact request quote, visually the primary content, truncated only in the list with expansion in detail.
3. Human reviewer identity; automated comments are available separately in Sources.
4. Text interpretation: “Follow-up to inspect”, “Possible response found” or “Needs interpretation”.
5. Small contextual labels such as “Question” or “Suggestion”.
6. Local reviewed marker, separate from all other state.

Default sort groups follow-up and unclear before possible responses, then deterministic chronology, with the sort rule visible. All groups remain present. Do not make the queue look empty by hiding possible responses silently. Persistently label the queue “Human review focus” and show “N automated comments in Sources”; all bot comments remain in Sources. Completeness refers to this labelled human-review scope, not automated findings. Filters display visible/total counts and provide one clear reset action. A filter yielding zero shows “No cards match these filters”, distinct from analysis yielding zero.

Do not display a numeric confidence badge unless it is empirically calibrated; verbal uncertainty belongs in the evidence panel. No green checkmark for model-associated responses. Local “Reviewed” may use a check accompanied by its precise label.

## 6. Evidence panel

The detail title repeats the specific request and source PR. A compact metadata line shows reviewer, date, comment kind and snapshot date. Then:

**Request evidence**: exact excerpt in a readable quotation block, “Open original on GitHub”, and “Show full comment”. Full comment is rendered as escaped text or safely sanitized Markdown, never arbitrary HTML.

**Possible response**: if present, show its author, later date, exact excerpt and independent source link. Label it “Possible response”, never “Resolution”. If absent, say “No relevant later response was identified in this snapshot. Inspect the conversation before acting.” Do not say no response exists.

**Why this is shown**: one short tentative model rationale, then explicit uncertainties. The original evidence appears before generated reasoning.

**GitHub reports**: actual review/thread/outdated state, separate visual container. Explain that resolved/outdated and approvals do not verify the implementation.

**Your local decision**: “Mark reviewed locally” / “Reopen”, plus optional note. Save feedback is inline and announced; failure retains typed note and offers retry. Clarify “This does not change GitHub.”

**Conversation context**: expand a date-ordered list of the PR's source comments. Preserve author/bot/type/date, with original links. Chronology baseline and full-source reading must be reachable without losing the selected request. Long bodies wrap with preserved whitespace and safe URL handling; use an explicit expansion rather than deeply nested scroll traps.

An invalid model citation is never shown in this panel as valid source evidence. Surface a rejected-output warning and allow original source reading/retry. Model-written external URLs never become clickable links.

## 7. Empty, partial and failure states

| State | UI copy and next action |
| --- | --- |
| No source selected | “Start with a few authored PRs” + sample/import actions |
| Valid source has no discussion | “No discussion in this snapshot” + source counts and original PR links |
| Analysis has zero cards | “No requests identified in this analysis” + inspect full sources / baseline; no celebratory completion |
| Filter hides all cards | “No cards match these filters” + reset filters |
| Partial import or cap | Persistent “Incomplete source coverage” banner listing affected PR/type, with source reading and retry; never dismissed by changing views |
| Model unavailable | “Local model is not available” + setup/retry + explicit baseline action |
| Timeout/invalid model output | Preserve source; state whether any analysis is usable; offer retry and original reading, never a silent baseline swap |
| API/offline failure | “Could not load saved results” + retry; do not replace previous source state with an apparently empty inbox |
| Corrupt snapshot | Explain validation failure in plain text, keep selected file name, show format guidance |
| GitHub denied/rate limit | Explain public/read-only scope, bounded retry or snapshot-import alternative; do not expose raw credentials/headers |
| Persist decision failed | Keep note unsaved, label it, offer retry; never toast success before confirmed save |
| New snapshot/analysis | Show new capture date and note that previous local decisions belong to the earlier analysis |

Warnings include concrete counts where available, e.g. “Read 80 of 120 available inline comments”, not invented totals. If total is unknown, state the cap and unknown remainder.

## 8. Motion and interaction

Use motion to explain a state change, not to delay work:

- Buttons: 120–160 ms colour/border transition, 1 px press displacement; no magnetic pointer or bouncing hover.
- Selected card: 140–180 ms background/border transition. Detail content may fade/translate 4 px for 160 ms on selection; focus remains stable.
- New source summary: single 200 ms staggered entrance capped at a few visible items; no repeated scroll-reveal hiding evidence.
- Saving a local decision: brief inline check/text change after confirmed persistence.
- Loading: subtle 1.5–2 second radar pulse confined to a small icon; text conveys state independently.
- Expand/collapse: no height animation that causes large layout jumps; standard disclosure is acceptable.

`prefers-reduced-motion: reduce` disables translation, pulse and reveal movement and shortens transitions. All source content is readable before any animation runs. Avoid parallax, 3D scroll stages, infinite canvas, audio, autoplay or heavy animation libraries. This is a repeat-use work tool whose distinctiveness should survive motion being disabled.

## 9. Accessibility and responsive acceptance

- Semantic header/main/aside/nav sections, one page-level heading, ordered headings and skip link.
- Standard buttons, links, labels and form controls. Request list items are selectable buttons with an explicit selected state; no nested interactive elements inside a button.
- Tab navigation alone reaches every action. Optional shortcuts may complement it but cannot replace it. Never intercept typing in text fields.
- A new detail view receives a deliberate heading focus only on mobile navigation; desktop selection must not unexpectedly steal focus from list navigation.
- Visible 2–3 px focus ring with adequate contrast; never remove outlines without a replacement.
- Minimum practical touch target 44×44 px for primary mobile actions. Icons have visible labels or accessible names.
- Status updates use polite live announcements; errors use an appropriate alert. Avoid announcing elapsed time every second.
- Do not encode interpretation, warning, bot status or selected state by colour alone.
- At 320 px width and 200% text zoom, controls wrap, evidence stays readable, and no page-wide horizontal scroll is introduced. Code/long IDs may scroll within their own labelled region only.
- Respect reduced motion; no hover-only content; links identify external destination. External source links use safe opener behaviour.

## 10. Usability review checklist

1. Can a first-time visitor distinguish public replay from a local live import before clicking anything?
2. Can they identify the exact original request and open its context within the selected evidence view?
3. Can they explain the difference between model interpretation, GitHub state and local reviewed status?
4. Can they find a possibly responded item after changing filters, and reach excluded automated comments in Sources?
5. Does incomplete coverage remain visible with zero cards and on mobile?
6. Can they recover from unavailable model, invalid snapshot and failed save without losing source/notes?
7. Does a zero-card view avoid falsely claiming that no work remains?
8. Can keyboard and reduced-motion users complete the entire workflow?
9. Can they export and understand exactly which dated source/analysis the sheet represents?
10. Does the screenshot/demo show the actual usable workflow rather than decorative UI with hidden limitations?

Record failures and fixes in the stage audit. Synthetic walkthroughs and agent-driven browser checks are engineering QA, not genuine-user validation.
