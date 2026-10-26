import { displayDate, validSourceUrl } from "./domain";
import type { CaptureChanges as Changes } from "./daily";

export function CaptureChanges({ changes }: { changes: Changes }) {
  const reviewer = changes.sources.filter((item) => item.role === "reviewer" && item.kind !== "missing").length;
  const author = changes.sources.filter((item) => item.role === "author" && item.kind !== "missing").length;
  return <section className="capture-changes panel" aria-labelledby="capture-changes-title">
    <h2 id="capture-changes-title">What changed since the previous capture?</h2>
    <p className="small-copy">Comparing {displayDate(changes.previousAt)} with {displayDate(changes.currentAt)}. These are source changes, not a judgement that requests were answered. Notes and reviewed choices stay with their original reading.</p>
    {!changes.complete && <p className="form-error">One or both captures have incomplete coverage. Missing sources or an empty comparison cannot establish that nothing changed.</p>}
    <p>{reviewer} new or changed reviewer comments · {author} new or changed author updates · {changes.states.length} PR changes</p>
    {!changes.sources.length && !changes.states.length && <p>No differences found in the captured content. This does not establish that no review work remains.</p>}
    {changes.states.length > 0 && <ul>{changes.states.map((item, index) => <li key={`${item.prId}:${index}`}><strong>{item.prId}</strong>: {item.description}</li>)}</ul>}
    {changes.sources.length > 0 && <details><summary>Inspect source changes ({changes.sources.length})</summary>
      {changes.sources.map((item) => <details className="capture-change" key={`${item.pr.id}:${item.comment.id}`}>
        <summary>{item.kind === "missing" ? "Absent from new capture" : item.kind === "new" ? "New" : "Changed"} {item.role} comment · {item.pr.id} · {item.comment.author}</summary>
        {item.kind === "missing" && <p>Previously captured; absent from this capture. It may be unavailable or outside captured coverage. Deletion is not established.</p>}
        {item.previous && <><h3>Earlier captured text</h3><blockquote>{item.previous.body || "No text on this source."}</blockquote></>}
        <h3>{item.kind === "missing" ? "Earlier captured text" : "Current captured text"}</h3>
        <blockquote>{item.comment.body || "No text on this source."}</blockquote>
        {item.previous && <p className="small-copy">Review state: {item.previous.review_state ?? "unavailable"} → {item.comment.review_state ?? "unavailable"}. Thread resolved: {String(item.previous.thread_resolved ?? "unavailable")} → {String(item.comment.thread_resolved ?? "unavailable")}. Outdated: {String(item.previous.thread_outdated ?? "unavailable")} → {String(item.comment.thread_outdated ?? "unavailable")}.</p>}
        {validSourceUrl(item.comment.url, item.pr) && <a href={item.comment.url} target="_blank" rel="noopener noreferrer">Open original on GitHub</a>}
      </details>)}
    </details>}
  </section>;
}
