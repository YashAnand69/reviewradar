import { useEffect, useRef, useState } from "react";
import type { FormEvent, ReactNode } from "react";
import { api } from "./api";
import {
  analysisWarnings,
  displayDate,
  exportReview,
  labels,
  parseUrls,
  sourceFor,
  validSourceUrl,
  verifiedCard,
  visibleCards,
} from "./domain";
import type {
  Analysis,
  Card,
  Disposition,
  Health,
  PullRequest,
  Sample,
  SavedAnalysis,
  Snapshot,
  SourceComment,
} from "./types";

const REPLAY = import.meta.env.VITE_REPLAY === "1";
const REPOSITORY = "https://github.com/YashAnand69/reviewradar";
type View = "review" | "sources";
function Glyph({
  name,
  className = "",
}: {
  name:
    | "arrow"
    | "plus"
    | "download"
    | "external"
    | "check"
    | "source"
    | "close"
    | "back"
    | "clock"
    | "search";
  className?: string;
}) {
  const paths = {
    arrow: <path d="M5 12h14m-6-6 6 6-6 6" />,
    plus: <path d="M12 5v14M5 12h14" />,
    download: (
      <>
        <path d="M12 3v12m-5-5 5 5 5-5M5 16v4h14v-4" />
      </>
    ),
    external: (
      <>
        <path d="M14 4h6v6m0-6L10 14M10 4H4v16h16v-6" />
      </>
    ),
    check: <path d="m5 12 4 4L19 6" />,
    source: (
      <>
        <path d="M5 3h10l4 4v14H5zM14 3v5h5M8 12h8M8 16h6" />
      </>
    ),
    close: <path d="m6 6 12 12M6 18 18 6" />,
    back: <path d="M19 12H5m6-6-6 6 6 6" />,
    clock: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 7v5l3 2" />
      </>
    ),
    search: (
      <>
        <circle cx="10" cy="10" r="6" />
        <path d="m15 15 5 5" />
      </>
    ),
  };
  return (
    <svg
      className={`glyph ${className}`}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name]}
    </svg>
  );
}
function Radar({ working = false }: { working?: boolean }) {
  return (
    <svg
      className={`radar ${working ? "working" : ""}`}
      viewBox="0 0 48 48"
      fill="none"
      aria-hidden="true"
    >
      <circle
        cx="24"
        cy="24"
        r="20"
        stroke="currentColor"
        strokeWidth="1.2"
        opacity=".4"
      />
      <circle
        cx="24"
        cy="24"
        r="12"
        stroke="currentColor"
        strokeWidth="1.2"
        opacity=".5"
      />
      <path
        d="M24 24 38 10M24 4v6M4 24h6M24 38v6M38 24h6"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      <circle cx="24" cy="24" r="3" fill="currentColor" />
      <circle cx="34" cy="16" r="3.5" fill="currentColor" />
    </svg>
  );
}
function External({ url, children }: { url: string; children: ReactNode }) {
  return (
    <a
      className="source-link"
      href={url}
      target="_blank"
      rel="noopener noreferrer"
    >
      {children}
      <Glyph name="external" />
      <span className="sr-only"> (opens GitHub in a new tab)</span>
    </a>
  );
}
function Note({
  title,
  children,
  kind = "info",
}: {
  title: string;
  children?: ReactNode;
  kind?: "info" | "warning" | "error";
}) {
  return (
    <section className={`notice ${kind}`} aria-label={title}>
      <strong>{title}</strong>
      {children && <div>{children}</div>}
    </section>
  );
}
function Modal({
  title,
  children,
  onClose,
  busy = false,
  returnFocusTo,
}: {
  title: string;
  children: ReactNode;
  onClose: () => void;
  busy?: boolean;
  returnFocusTo?: HTMLElement | null;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const opener =
      returnFocusTo ??
      (document.activeElement instanceof HTMLElement
        ? document.activeElement
        : null);
    ref.current?.showModal();
    return () => {
      ref.current?.close();
      if (opener?.isConnected) opener.focus();
    };
  }, []);
  return (
    <dialog
      ref={ref}
      className="modal"
      aria-labelledby="modal-title"
      onCancel={(event) => {
        event.preventDefault();
        if (!busy) onClose();
      }}
    >
      <header>
        <div>
          <p className="eyebrow">YOUR WORKSPACE</p>
          <h2 id="modal-title">{title}</h2>
        </div>
        <button
          className="icon-button"
          aria-label="Close dialog"
          disabled={busy}
          onClick={onClose}
        >
          <Glyph name="close" />
        </button>
      </header>
      {children}
    </dialog>
  );
}

function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [connected, setConnected] = useState(false);
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const activeAnalysisId = useRef<string | null>(null);
  const [manifest, setManifest] = useState<Record<string, unknown> | null>(
    null,
  );
  const [decisions, setDecisions] = useState<Record<string, Disposition>>({});
  const [selected, setSelected] = useState<string | null>(null);
  const [view, setView] = useState<View>("review");
  const [interpretation, setInterpretation] = useState("all");
  const [prFilter, setPrFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [includeReviewed, setIncludeReviewed] = useState(true);
  const [busy, setBusy] = useState("");
  const drafts = useRef<Record<string, string>>({});
  const [resetVersion, setResetVersion] = useState(0);
  const [elapsed, setElapsed] = useState(0);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const [showImport, setShowImport] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const historyOpener = useRef<HTMLButtonElement>(null);
  const [history, setHistory] = useState<SavedAnalysis[]>([]);
  const [owner, setOwner] = useState("");
  const [urlText, setUrlText] = useState("");
  const [importError, setImportError] = useState("");
  const [isSavedRun, setIsSavedRun] = useState(false);
  const [mobileDetail, setMobileDetail] = useState(false);
  const busyRef = useRef(false);
  const selectedHeading = useRef<HTMLHeadingElement>(null);

  function resetFilters() {
    setInterpretation("all");
    setPrFilter("all");
    setSearch("");
    setIncludeReviewed(true);
  }
  function install(
    nextSnapshot: Snapshot,
    nextAnalysis: Analysis | null,
    nextDecisions: Disposition[] = [],
    saved = false,
    nextManifest: Record<string, unknown> | null = null,
  ) {
    setSnapshot(nextSnapshot);
    activeAnalysisId.current = nextAnalysis?.id ?? null;
    setAnalysis(nextAnalysis);
    setDecisions(Object.fromEntries(nextDecisions.map((d) => [d.card_id, d])));
    setSelected(nextAnalysis?.cards[0]?.id ?? null);
    setView("review");
    setMobileDetail(false);
    setIsSavedRun(saved);
    setManifest(nextManifest);
    resetFilters();
  }
  async function operation(label: string, work: () => Promise<void>) {
    if (busyRef.current) return;
    busyRef.current = true;
    setBusy(label);
    setElapsed(0);
    setError("");
    setStatus("");
    try {
      await work();
    } catch (cause) {
      const message =
        cause instanceof Error
          ? cause.message
          : "This action could not be completed. Retry or inspect the original sources.";
      if (showImport) setImportError(message);
      else setError(message);
    } finally {
      busyRef.current = false;
      setBusy("");
    }
  }
  async function connect() {
    await operation("Connecting to the local workspace", async () => {
      const result = await api.connect();
      setHealth(result);
      setConnected(true);
      setStatus("Local workspace connected. Sources stay on this computer.");
    });
  }
  async function loadSample() {
    await operation(
      REPLAY
        ? "Opening the historical replay"
        : "Loading the saved historical sample",
      async () => {
        let packet: Sample;
        if (REPLAY) {
          const response = await fetch(
            `${import.meta.env.BASE_URL}sample.json`,
            { cache: "no-cache" },
          );
          if (!response.ok)
            throw new Error(
              "The published sample is unavailable. Please use the source repository for local setup; this page will not invent sample results.",
            );
          packet = await response.json();
        } else {
          const data = await api.sample();
          packet = "snapshot" in data ? data : { snapshot: data };
        }
        if (!packet.snapshot?.prs || !Array.isArray(packet.snapshot.prs))
          throw new Error(
            "The sample data is invalid. Please check the published release.",
          );
        let loaded: Disposition[] = [];
        if (packet.analysis) {
          if (REPLAY) {
            try {
              const raw = localStorage.getItem(
                `reviewradar:${packet.analysis.id}`,
              );
              loaded = raw ? JSON.parse(raw) : [];
              if (!Array.isArray(loaded)) loaded = [];
            } catch {
              loaded = [];
              setStatus(
                "Your browser could not restore replay decisions. Source evidence is still available.",
              );
            }
          } else loaded = await api.dispositions(packet.analysis.id);
        }
        install(
          packet.snapshot,
          packet.analysis ?? null,
          loaded,
          !!packet.analysis,
          packet.manifest ?? null,
        );
      },
    );
  }
  useEffect(() => {
    if (REPLAY) void loadSample();
    else void connect();
  }, []);
  useEffect(() => {
    if (!busy) return;
    const start = Date.now();
    const timer = window.setInterval(
      () => setElapsed(Math.floor((Date.now() - start) / 1000)),
      1000,
    );
    return () => window.clearInterval(timer);
  }, [busy]);
  const cards =
    analysis && snapshot
      ? analysis.cards.filter((c) => verifiedCard(snapshot, c, analysis.mode))
      : [];
  const rejectedCount = analysis ? analysis.cards.length - cards.length : 0;
  const filtered = visibleCards(cards, decisions, {
    interpretation,
    pr: prFilter,
    includeReviewed,
    search,
  });
  const selectedCard =
    filtered.find((c) => c.id === selected) ?? filtered[0] ?? null;
  useEffect(() => {
    if (
      view === "review" &&
      mobileDetail &&
      window.matchMedia("(max-width: 800px)").matches
    )
      selectedHeading.current?.focus();
  }, [mobileDetail, selectedCard?.id, view]);
  const reviewedCount = cards.filter(
    (c) => decisions[c.id]?.state === "reviewed",
  ).length;
  const botCount =
    snapshot?.prs.reduce(
      (count, pr) => count + pr.comments.filter((c) => c.is_bot).length,
      0,
    ) ?? 0;
  const warnings = snapshot ? analysisWarnings(snapshot, analysis) : [];
  if (rejectedCount)
    warnings.push(
      `${rejectedCount} card${rejectedCount === 1 ? " was" : "s were"} rejected because source evidence could not be verified. Inspect Sources; this view is incomplete.`,
    );
  const isBaseline = analysis?.mode === "baseline";

  async function githubImport(event: FormEvent) {
    event.preventDefault();
    setImportError("");
    let urls: string[];
    try {
      if (!/^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$/.test(owner.trim()))
        throw new Error("Enter a valid GitHub account name.");
      urls = parseUrls(urlText);
    } catch (cause) {
      setImportError((cause as Error).message);
      return;
    }
    await operation("Reading public GitHub discussions", async () => {
      const next = await api.importGithub(owner.trim(), urls);
      install(next, null);
      setShowImport(false);
      setStatus(
        "Snapshot imported. Inspect coverage, then choose a local analysis mode.",
      );
    });
  }
  async function fileImport(file: File | undefined) {
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) {
      setImportError(
        "Choose a snapshot under 2 MiB. Larger files are not accepted.",
      );
      return;
    }
    setImportError("");
    await operation("Validating and importing your snapshot", async () => {
      let parsed: unknown;
      try {
        parsed = JSON.parse(await file.text());
      } catch {
        throw new Error(
          "This file is not valid JSON. Use an exported ReviewRadar snapshot.",
        );
      }
      const value =
        parsed && typeof parsed === "object" && "snapshot" in parsed
          ? (parsed as { snapshot: unknown }).snapshot
          : parsed;
      const next = await api.importSnapshot(value);
      install(next, null);
      setShowImport(false);
      setStatus(
        "Imported snapshot saved locally. Imported source authenticity has not been independently verified.",
      );
    });
  }
  async function run(mode: "model" | "baseline") {
    if (!snapshot) return;
    await operation(
      mode === "model"
        ? "Reading human review locally"
        : "Preparing the chronology baseline",
      async () => {
        const result = await api.analyse(snapshot.id, mode);
        activeAnalysisId.current = result.id;
        setAnalysis(result);
        setDecisions({});
        setSelected(result.cards[0]?.id ?? null);
        setIsSavedRun(false);
        setManifest(null);
        setMobileDetail(false);
        resetFilters();
        setStatus(
          result.complete
            ? "Analysis finished for the stated human-review scope. Inspect the evidence before deciding."
            : "Analysis finished with incomplete coverage. Inspect the warnings and sources.",
        );
      },
    );
  }
  async function save(card: Card, state: "open" | "reviewed", note: string) {
    if (!analysis) return;
    setError("");
    setStatus("");
    const disposition: Disposition = {
      analysis_id: analysis.id,
      card_id: card.id,
      state,
      note,
      updated_at: new Date().toISOString(),
    };
    try {
      let saved: Disposition;
      if (REPLAY) {
        const next = { ...decisions, [card.id]: disposition };
        localStorage.setItem(
          `reviewradar:${analysis.id}`,
          JSON.stringify(Object.values(next)),
        );
        saved = disposition;
      } else saved = await api.save(analysis.id, card.id, state, note);
      // A slow save belongs to the analysis that started it, even if a new
      // result with the same deterministic card ID has since been opened.
      if (activeAnalysisId.current !== disposition.analysis_id) return;
      setDecisions((old) => ({ ...old, [card.id]: saved }));
      setStatus(
        REPLAY
          ? "Saved in this browser only. GitHub was not changed."
          : "Saved locally. GitHub was not changed.",
      );
    } catch (cause) {
      if (activeAnalysisId.current !== disposition.analysis_id) return;
      setError(
        cause instanceof Error
          ? cause.message
          : "Your decision could not be saved. The note remains in the editor.",
      );
      throw cause;
    }
  }
  async function download() {
    if (!snapshot || !analysis) return;
    await operation("Preparing your review sheet", async () => {
      const blob = REPLAY
        ? new Blob([exportReview(snapshot, analysis, decisions)], {
            type: "text/markdown;charset=utf-8",
          })
        : await api.export(analysis.id);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `reviewradar-${analysis.id.slice(0, 12)}.md`;
      link.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
      setStatus(
        "Review sheet downloaded. It includes source dates, uncertainty and local decisions.",
      );
    });
  }
  function downloadSnapshot() {
    if (!snapshot) return;
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(snapshot, null, 2)], {
        type: "application/json",
      }),
    );
    const link = document.createElement("a");
    link.href = url;
    link.download = `reviewradar-source-${snapshot.id.slice(0, 12)}.json`;
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    setStatus(
      "Source snapshot downloaded. It may include public discussion text; review before sharing.",
    );
  }
  async function openHistory() {
    setShowHistory(true);
    await operation("Loading saved analyses", async () =>
      setHistory(await api.history()),
    );
  }
  async function restore(id: string) {
    await operation("Restoring a saved analysis", async () => {
      const next = await api.analysis(id);
      const [source, localDecisions] = await Promise.all([
        api.snapshot(next.snapshot_id),
        api.dispositions(id),
      ]);
      install(source, next, localDecisions, true);
      setShowHistory(false);
      setStatus("Saved analysis restored with its original capture date.");
    });
  }
  function resetReplay() {
    if (!analysis) return;
    try {
      localStorage.removeItem(`reviewradar:${analysis.id}`);
      setDecisions({});
      for (const key of Object.keys(drafts.current))
        if (key.startsWith(`${analysis.id}:`)) delete drafts.current[key];
      setResetVersion((old) => old + 1);
      setStatus(
        "Replay decisions reset in this browser. The historical source is unchanged.",
      );
    } catch {
      setError("Your browser did not allow replay storage to be reset.");
    }
  }

  return (
    <>
      <a className="skip" href="#main">
        Skip to workspace
      </a>
      <header className="topbar">
        <a className="brand" href="#main" aria-label="ReviewRadar workspace">
          <Radar />
          <span>
            Review<span className="brand-light">Radar</span>
            <small>READ ONCE. KEEP THE EVIDENCE.</small>
          </span>
        </a>
        <div className="header-actions">
          <span className={`mode-badge ${REPLAY ? "replay" : ""}`}>
            <i />
            {REPLAY
              ? "Historical replay"
              : connected
                ? "Local workspace"
                : "Local connection needed"}
          </span>
          <button className="text-button" onClick={() => setShowHelp(true)}>
            How it works
          </button>
          <a
            className="repository-link"
            href={REPOSITORY}
            target="_blank"
            rel="noopener noreferrer"
          >
            Source <Glyph name="external" />
          </a>
        </div>
      </header>
      <main id="main" tabIndex={-1}>
        <section className="intro">
          <div>
            <p className="eyebrow">
              A LITTLE LESS REREADING. A CLEARER NEXT LOOK.
            </p>
            <h1>
              Keep the request.
              <br className="small-break" /> Find the <span>context.</span>
            </h1>
            <p className="intro-copy">
              Human review requests, possible replies, and the original
              evidence.
              <br className="desktop-break" /> Your judgement stays at the
              centre. GitHub stays untouched.
            </p>
          </div>
          <div className="intro-actions">
            {!REPLAY && (
              <>
                <button
                  className="button primary"
                  disabled={!connected || !!busy}
                  onClick={() => setShowImport(true)}
                >
                  <Glyph name="plus" />
                  Import your PRs
                </button>
                <button
                  ref={historyOpener}
                  className="text-button"
                  disabled={!connected || !!busy}
                  onClick={() => void openHistory()}
                >
                  <Glyph name="clock" />
                  Saved analyses
                </button>
              </>
            )}
            {REPLAY && (
              <a
                className="button primary"
                href={`${REPOSITORY}#run-locally`}
                target="_blank"
                rel="noopener noreferrer"
              >
                Run the local app
                <Glyph name="arrow" />
              </a>
            )}
          </div>
        </section>
        {REPLAY && (
          <Note title="A real historical sample, not a live inbox">
            <p>
              This public preview displays saved evidence and a saved analysis.
              It does not fetch your GitHub data or run a model online.
              Decisions stay in this browser.{" "}
              <a href={REPOSITORY} target="_blank" rel="noopener noreferrer">
                Get the working local app.
              </a>
            </p>
          </Note>
        )}
        {error && (
          <div className="error-block" role="alert">
            <span>
              <strong>This action did not finish.</strong> {error}
            </span>
            <button
              className="icon-button"
              aria-label="Dismiss error"
              onClick={() => setError("")}
            >
              <Glyph name="close" />
            </button>
            {!connected && !REPLAY && (
              <button
                className="button small"
                disabled={!!busy}
                onClick={() => void connect()}
              >
                Retry connection
              </button>
            )}
            {REPLAY && !snapshot && (
              <button
                className="button small"
                disabled={!!busy}
                onClick={() => void loadSample()}
              >
                Retry sample
              </button>
            )}
          </div>
        )}
        <div className="live-status" role="status" aria-live="polite">
          {status}
        </div>
        {busy && (
          <div className="processing" role="status">
            <Radar working />
            <div>
              <strong>{busy}…</strong>
              <p>
                {busy.includes("review")
                  ? "The model is reading the selected human conversation. Nothing will be posted."
                  : "Keep this window open while the local operation completes."}
              </p>
            </div>
            <span aria-hidden="true">{elapsed}s elapsed</span>
          </div>
        )}
        {!snapshot && !busy && (
          <section className="welcome panel">
            <div className="welcome-art">
              <Radar />
              <span className="art-line" />
              <span className="art-word">request</span>
              <span className="art-line dotted" />
              <span className="art-word muted">possible reply</span>
            </div>
            <div>
              <p className="eyebrow">START WITH THE CONVERSATION</p>
              <h2>
                The feedback is there.
                <br />
                The thread can be a lot.
              </h2>
              <p>
                Open a real public example to see a review request beside a
                possible later response. Then inspect the original and decide
                what deserves another look.
              </p>
              <button
                className="button primary"
                disabled={!REPLAY && !connected}
                onClick={() => void loadSample()}
              >
                Explore the historical sample
                <Glyph name="arrow" />
              </button>
              <p className="small-copy">
                No sign-in for the sample. No automatic replies or fixes.
              </p>
            </div>
          </section>
        )}
        {snapshot && (
          <>
            <section className="snapshot-bar panel">
              <div className="snapshot-heading">
                <span className="document-icon">
                  <Glyph name="source" />
                </span>
                <div>
                  <h2>{snapshot.owner}'s selected conversations</h2>
                  <p>
                    {snapshot.prs.length} public PR
                    {snapshot.prs.length !== 1 ? "s" : ""} · Captured{" "}
                    {displayDate(snapshot.fetched_at)} ·{" "}
                    {snapshot.source === "import"
                      ? "Imported evidence · authenticity not verified"
                      : snapshot.source === "synthetic"
                        ? "Synthetic test material"
                        : "Public GitHub snapshot"}
                  </p>
                </div>
              </div>
              <div className="snapshot-actions">
                <span
                  className={`coverage-label ${snapshot.complete ? "" : "caution"}`}
                >
                  {snapshot.complete
                    ? "Source intake complete"
                    : "Source intake incomplete"}
                </span>
                <button
                  className="button small"
                  onClick={() => setView("sources")}
                >
                  Inspect sources
                  <Glyph name="arrow" />
                </button>
                <button className="text-button" onClick={downloadSnapshot}>
                  Save source JSON
                  <Glyph name="download" />
                </button>
              </div>
            </section>
            {!!warnings.length && (
              <Note
                kind="warning"
                title="Incomplete coverage — inspect the sources"
              >
                <p>
                  Some source context or analysis is missing. These results do
                  not establish that a PR is clear of review work.
                </p>
                <details className="coverage-details">
                  <summary>View coverage details ({warnings.length})</summary>
                  <ul>
                    {warnings.map((warning, index) => (
                      <li key={`${index}:${warning}`}>{warning}</li>
                    ))}
                  </ul>
                </details>
              </Note>
            )}
            <div className="scope-bar">
              <span>
                <span className="scope-dot" />
                Human review focus
              </span>
              <button
                className="text-button"
                onClick={() => setView("sources")}
              >
                {botCount} automated comment{botCount !== 1 ? "s" : ""}{" "}
                available in Sources
                <Glyph name="arrow" />
              </button>
            </div>
            <div className="workspace-tabs">
              <nav aria-label="Workspace view">
                <button
                  className={view === "review" ? "active" : ""}
                  aria-current={view === "review" ? "page" : undefined}
                  onClick={() => setView("review")}
                >
                  Review queue <span>{cards.length}</span>
                </button>
                <button
                  className={view === "sources" ? "active" : ""}
                  aria-current={view === "sources" ? "page" : undefined}
                  onClick={() => setView("sources")}
                >
                  Sources{" "}
                  <span>
                    {snapshot.prs.reduce((n, p) => n + p.comments.length, 0)}
                  </span>
                </button>
              </nav>
              <div className="analysis-actions">
                {analysis && (
                  <span className="analysis-mode">
                    {isSavedRun ? "Saved " : ""}
                    {isBaseline
                      ? "chronology baseline"
                      : (analysis.model ?? "local model")}
                    {analysis.complete
                      ? " · human scope processed"
                      : " · incomplete"}
                  </span>
                )}
                {!REPLAY && (
                  <>
                    <button
                      className="button small"
                      disabled={!!busy}
                      onClick={() => void run("baseline")}
                    >
                      Chronology baseline
                    </button>
                    <button
                      className="button primary small"
                      disabled={!!busy || !health?.model_configured}
                      title={
                        !health?.model_configured
                          ? "Configure the local model to enable inference"
                          : undefined
                      }
                      onClick={() => void run("model")}
                    >
                      Analyse locally
                      <Glyph name="arrow" />
                    </button>
                  </>
                )}
                {analysis && (
                  <button
                    className="icon-button outlined"
                    aria-label="Download review sheet"
                    title="Download review sheet"
                    disabled={!!busy}
                    onClick={() => void download()}
                  >
                    <Glyph name="download" />
                  </button>
                )}
              </div>
            </div>
            {!REPLAY && !health?.model_configured && (
              <Note title="Local model is not configured">
                <p>
                  You can inspect all source evidence and explicitly choose the
                  chronology baseline. The baseline does not identify semantic
                  requests or match replies.{" "}
                  <a
                    href={`${REPOSITORY}#run-locally`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Local model setup
                  </a>
                </p>
              </Note>
            )}
            {view === "sources" ? (
              <Sources snapshot={snapshot} />
            ) : !analysis ? (
              <section className="empty panel">
                <Radar />
                <h2>Your sources are ready.</h2>
                <p>
                  Inspect the source coverage, then run the local model to
                  extract human requests and possible later replies. The
                  chronology baseline is a separate, no-model reading list.
                </p>
                {REPLAY && (
                  <p>
                    This replay has no saved analysis. Source evidence is still
                    available; no result is being invented.
                  </p>
                )}
                <button className="button" onClick={() => setView("sources")}>
                  Read the source conversations
                </button>
              </section>
            ) : (
              <>
                <section className="analysis-caption">
                  <div>
                    <h2>
                      {isBaseline
                        ? "Comments to inspect"
                        : "A clearer place to pick up"}
                    </h2>
                    <p>
                      {isBaseline
                        ? "A deterministic human-comment list. No semantic request or response judgement."
                        : "Original words first. A possible response is a lead to inspect, never proof of a fix."}
                    </p>
                  </div>
                  <span>
                    {cards.length} {isBaseline ? "comment" : "card"}
                    {cards.length !== 1 && "s"} · {reviewedCount} reviewed
                    locally
                  </span>
                </section>
                <div
                  className={`workbench ${mobileDetail ? "show-detail" : ""}`}
                >
                  <section
                    className="request-list panel"
                    aria-label={
                      isBaseline ? "Comments to inspect" : "Review request list"
                    }
                  >
                    <div className="list-controls">
                      <label className="search-field">
                        <Glyph name="search" />
                        <span className="sr-only">Search request evidence</span>
                        <input
                          value={search}
                          placeholder={
                            isBaseline ? "Find a comment…" : "Find a request…"
                          }
                          onChange={(event) => setSearch(event.target.value)}
                        />
                      </label>
                      <div className="filter-row">
                        <label>
                          <span className="sr-only">Filter by PR</span>
                          <select
                            value={prFilter}
                            onChange={(event) =>
                              setPrFilter(event.target.value)
                            }
                          >
                            <option value="all">All pull requests</option>
                            {snapshot.prs.map((pr) => (
                              <option key={pr.id} value={pr.id}>
                                {pr.id}
                              </option>
                            ))}
                          </select>
                        </label>
                        <label>
                          <span className="sr-only">
                            Filter by interpretation
                          </span>
                          <select
                            value={interpretation}
                            onChange={(event) =>
                              setInterpretation(event.target.value)
                            }
                            disabled={isBaseline}
                          >
                            <option value="all">All interpretations</option>
                            <option value="follow_up">Follow-up</option>
                            <option value="possibly_responded">
                              Possible response
                            </option>
                            <option value="unclear">Unclear</option>
                          </select>
                        </label>
                      </div>
                      <label className="checkbox">
                        <input
                          type="checkbox"
                          checked={includeReviewed}
                          onChange={(event) =>
                            setIncludeReviewed(event.target.checked)
                          }
                        />
                        Include reviewed locally
                      </label>
                      <div className="list-count">
                        <span>
                          {filtered.length} of {cards.length} shown
                        </span>
                        <span>Follow-up & unclear first</span>
                      </div>
                    </div>
                    <div className="cards">
                      {filtered.map((card) => {
                        const source = sourceFor(snapshot, card).request;
                        return (
                          <button
                            key={card.id}
                            className={`request-card ${selectedCard?.id === card.id ? "selected" : ""}`}
                            aria-pressed={selectedCard?.id === card.id}
                            onClick={() => {
                              setSelected(card.id);
                              setMobileDetail(true);
                            }}
                          >
                            <span className="card-top">
                              <span>{card.pr_id}</span>
                              <Glyph name="arrow" />
                            </span>
                            <span className="card-quote">
                              {card.request.quote}
                            </span>
                            <span className="card-author">
                              {source?.author ?? "Unknown author"} ·{" "}
                              {card.category === "unclear"
                                ? "Comment"
                                : card.category}
                            </span>
                            <span className="card-bottom">
                              <span
                                className={`interpretation ${card.interpretation}`}
                              >
                                {isBaseline
                                  ? "Comment to inspect"
                                  : labels[card.interpretation]}
                              </span>
                              {decisions[card.id]?.state === "reviewed" && (
                                <span className="local-check">
                                  <Glyph name="check" />
                                  Reviewed locally
                                </span>
                              )}
                            </span>
                          </button>
                        );
                      })}
                      {!filtered.length && (
                        <div className="list-empty">
                          <h3>
                            {cards.length
                              ? "No cards match these filters."
                              : isBaseline
                                ? "No human reviewer comments in this view."
                                : "No requests identified in this analysis."}
                          </h3>
                          <p>
                            {cards.length
                              ? "Reset the filters to return to all evidence."
                              : "This is not proof that no work remains. Inspect the complete original sources, including automated comments."}
                          </p>
                          {cards.length ? (
                            <button
                              className="button small"
                              onClick={resetFilters}
                            >
                              Reset filters
                            </button>
                          ) : (
                            <button
                              className="button small"
                              onClick={() => setView("sources")}
                            >
                              Inspect Sources
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  </section>
                  <section
                    className="evidence-panel panel"
                    aria-label="Selected evidence"
                  >
                    <button
                      className="text-button mobile-back"
                      onClick={() => setMobileDetail(false)}
                    >
                      <Glyph name="back" />
                      Back to requests
                    </button>
                    {selectedCard ? (
                      <Evidence
                        key={`${analysis.id}:${selectedCard.id}:${resetVersion}`}
                        headingRef={selectedHeading}
                        card={selectedCard}
                        snapshot={snapshot}
                        baseline={isBaseline}
                        decision={decisions[selectedCard.id]}
                        replay={REPLAY}
                        draft={
                          drafts.current[`${analysis.id}:${selectedCard.id}`]
                        }
                        onDraft={(value) => {
                          drafts.current[`${analysis.id}:${selectedCard.id}`] =
                            value;
                        }}
                        onSave={save}
                      />
                    ) : (
                      <div className="evidence-empty">
                        <span className="document-icon">
                          <Glyph name="source" />
                        </span>
                        <h2 ref={selectedHeading} tabIndex={-1}>
                          Select evidence to inspect
                        </h2>
                        <p>
                          {cards.length
                            ? "Choose a card to read its request and possible response side by side."
                            : "No evidence card is selected. The Sources view contains the original conversation and any excluded automated comments."}
                        </p>
                        <button
                          className="text-button"
                          onClick={() => setView("sources")}
                        >
                          Open Sources
                          <Glyph name="arrow" />
                        </button>
                      </div>
                    )}
                  </section>
                </div>
                <div className="run-provenance">
                  <span>
                    <Glyph name="clock" />
                    Analysis saved {displayDate(analysis.created_at)} ·{" "}
                    {analysis.stats.elapsed_seconds.toFixed(1)}s recorded
                    runtime
                  </span>
                  <span>
                    {analysis.stats.comments_processed} human comments processed
                    · {analysis.stats.comments_excluded_bots ?? botCount}{" "}
                    automated excluded
                  </span>
                </div>
              </>
            )}
            {REPLAY && analysis && (
              <div className="replay-reset">
                <p>
                  Review choices are stored only in this browser for this saved
                  analysis.
                </p>
                <button className="text-button" onClick={resetReplay}>
                  Reset my replay choices
                </button>
              </div>
            )}
            {manifest && (
              <details className="manifest">
                <summary>Sample provenance and run details</summary>
                <pre>{JSON.stringify(manifest, null, 2)}</pre>
              </details>
            )}
          </>
        )}
      </main>
      <footer className="footer">
        <div className="footer-brand">
          <Radar />
          <span>ReviewRadar</span>
        </div>
        <p>Evidence beside interpretation. The final decision is yours.</p>
        <button className="text-button" onClick={() => setShowHelp(true)}>
          Scope & privacy
        </button>
      </footer>
      {showImport && (
        <Modal
          title="Bring a few conversations."
          onClose={() => setShowImport(false)}
          busy={!!busy}
        >
          <p className="modal-copy">
            Read-only, public PRs authored by one account. GitHub credentials
            remain in your local CLI. No comments, code or review states will be
            changed.
          </p>
          <form onSubmit={(event) => void githubImport(event)}>
            <label className="field">
              GitHub account
              <input
                autoComplete="off"
                value={owner}
                onChange={(event) => setOwner(event.target.value)}
                placeholder="Your GitHub handle"
                required
                disabled={!!busy}
              />
            </label>
            <label className="field">
              Pull-request URLs
              <textarea
                rows={4}
                value={urlText}
                onChange={(event) => setUrlText(event.target.value)}
                placeholder={
                  "https://github.com/owner/repo/pull/123\nOne URL per line · up to five public PRs"
                }
                required
                disabled={!!busy}
              />
            </label>
            {importError && (
              <p className="form-error" role="alert">
                {importError}
              </p>
            )}
            <button
              className="button primary"
              type="submit"
              disabled={!!busy || !health?.github_available}
            >
              {busy ? "Reading sources…" : "Import public discussions"}
              <Glyph name="arrow" />
            </button>
            {!health?.github_available && (
              <p className="small-copy">
                GitHub CLI is unavailable. Use a saved snapshot below or finish
                local setup.
              </p>
            )}
          </form>
          <div className="import-divider">
            <span>or use an existing snapshot</span>
          </div>
          <label className="file-field">
            <Glyph name="source" />
            <span>
              <strong>Import snapshot JSON</strong>
              <small>
                Up to 2 MiB. Imported evidence is not authenticated by
                ReviewRadar.
              </small>
            </span>
            <input
              type="file"
              accept=".json,application/json"
              disabled={!!busy}
              onChange={(event) => void fileImport(event.target.files?.[0])}
            />
          </label>
        </Modal>
      )}
      {showHistory && (
        <Modal
          title="Return to an earlier reading."
          onClose={() => setShowHistory(false)}
          busy={!!busy}
          returnFocusTo={historyOpener.current}
        >
          <p className="modal-copy">
            Each analysis stays bound to its original snapshot. Loading it does
            not refresh GitHub or apply decisions to newer evidence.
          </p>
          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}
          {!history.length && !busy && (
            <p className="empty-copy">
              No saved analyses yet. Import a source and run a baseline or local
              model first.
            </p>
          )}
          <div className="history-list">
            {history.map((item) => (
              <button
                key={item.id}
                className="history-item"
                disabled={!!busy}
                onClick={() => void restore(item.id)}
              >
                <span>
                  <strong>
                    {item.mode === "baseline"
                      ? "Chronology baseline"
                      : (item.model ?? "Local model")}
                  </strong>
                  <small>
                    {displayDate(item.created_at)} · {item.id.slice(0, 12)}
                  </small>
                </span>
                <Glyph name="arrow" />
              </button>
            ))}
          </div>
        </Modal>
      )}
      {showHelp && (
        <Modal
          title="A reading aid. Your judgement."
          onClose={() => setShowHelp(false)}
        >
          <div className="help-content">
            <section>
              <h3>1. Start with selected public PRs</h3>
              <p>
                The local app reads discussions authored by your selected GitHub
                account. Capture dates and missing coverage stay visible.
                Snapshot imports are user-supplied evidence, not authenticated
                GitHub records.
              </p>
            </section>
            <section>
              <h3>2. Inspect the human request and possible reply</h3>
              <p>
                A local model proposes evidence pairs. Original quotes are
                validated, but a valid quote can still be interpreted
                incorrectly. Automated comments are excluded from the human
                queue and remain available in Sources.
              </p>
            </section>
            <section>
              <h3>3. Decide locally</h3>
              <p>
                “Reviewed locally” organizes your own reading. It does not
                resolve a thread, approve code, verify a fix or notify anyone.
                New analyses have independent decisions.
              </p>
            </section>
            <section>
              <h3>What stays local</h3>
              <p>
                Inference, imported snapshots, notes and decisions stay on this
                computer in local mode. Fresh GitHub intake needs internet.
                There is no hosted model call or telemetry. Public replay uses
                deliberately published historical data; its decisions are stored
                in this browser only.
              </p>
            </section>
            <section>
              <h3>Data and limits</h3>
              <p>
                The first release accepts up to five public PRs. Large
                conversations can be rejected with visible coverage warnings.
                Delete local data using the README procedure; downloaded exports
                and public samples are not deleted with the database.
              </p>
              <a href={REPOSITORY} target="_blank" rel="noopener noreferrer">
                Setup, data deletion, model provenance and evaluation
                <Glyph name="external" />
              </a>
            </section>
          </div>
        </Modal>
      )}
    </>
  );
}

function Evidence({
  card,
  snapshot,
  baseline,
  decision,
  replay,
  draft,
  onDraft,
  onSave,
  headingRef,
}: {
  card: Card;
  snapshot: Snapshot;
  baseline: boolean;
  decision: Disposition | undefined;
  replay: boolean;
  draft: string | undefined;
  onDraft: (value: string) => void;
  onSave: (
    card: Card,
    state: "open" | "reviewed",
    note: string,
  ) => Promise<void>;
  headingRef: React.RefObject<HTMLHeadingElement | null>;
}) {
  const { pr, request, response } = sourceFor(snapshot, card);
  const [note, setNote] = useState(draft ?? decision?.note ?? "");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState("");
  if (!pr || !request)
    return (
      <Note
        kind="error"
        title="This evidence could not be found in its snapshot."
      />
    );
  const dirty = note !== (decision?.note ?? "");
  async function persist(state: "open" | "reviewed") {
    setSaving(true);
    setSaved("");
    try {
      await onSave(card, state, note);
      setSaved("Saved. GitHub was not changed.");
    } catch {
      setSaved("Not saved. Your note remains here; retry when ready.");
    } finally {
      setSaving(false);
    }
  }
  return (
    <article className="evidence-content">
      <header className="evidence-heading">
        <p className="eyebrow">
          {baseline ? "SOURCE COMMENT" : "THE EVIDENCE"}
        </p>
        <h2 ref={headingRef} tabIndex={-1}>
          {pr.title}
        </h2>
        <div className="pr-meta">
          <External url={pr.url}>{pr.id}</External>
          <span className={`pr-state ${pr.state.toLowerCase()}`}>
            {pr.state.toLowerCase()}
          </span>
        </div>
        <p className="evidence-caveat">
          {baseline
            ? "A comment to read, not a model-identified request."
            : "A possible response is a lead to inspect. It is not a verified fix."}
        </p>
      </header>
      {response &&
        Date.parse(request.updated_at) > Date.parse(response.created_at) && (
          <Note kind="warning" title="The request was edited after this reply">
            <p>
              The original wording at reply time is unknown. Compare the current
              source carefully before interpreting this pair.
            </p>
          </Note>
        )}
      <div className="paired-evidence">
        <EvidenceQuote
          title={baseline ? "Comment to inspect" : "Original request"}
          source={request}
          quote={card.request.quote}
          pr={pr}
        />
        {!baseline && (
          <EvidenceQuote
            title="Possible later response"
            source={response}
            quote={card.response?.quote}
            pr={pr}
          />
        )}
      </div>
      {!baseline && (
        <section className="interpretation-box">
          <div className="section-heading">
            <h3>Why this is shown</h3>
            <span className={`interpretation ${card.interpretation}`}>
              {labels[card.interpretation]}
            </span>
          </div>
          <p>{card.rationale}</p>
          {!!card.uncertainty.length && (
            <ul>
              {card.uncertainty.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          )}
          <p className="small-copy">
            Model interpretation. Read the surrounding conversation before
            acting.
          </p>
        </section>
      )}
      <section className="github-state">
        <h3>GitHub reports</h3>
        <dl>
          <div>
            <dt>Review on this source</dt>
            <dd>
              {card.github.review_state?.replaceAll("_", " ").toLowerCase() ??
                "No review state recorded"}
            </dd>
          </div>
          <div>
            <dt>Thread</dt>
            <dd>
              {card.github.thread_resolved === null
                ? "Not available"
                : card.github.thread_resolved
                  ? "Resolved on GitHub"
                  : "Not resolved on GitHub"}
            </dd>
          </div>
          <div>
            <dt>Outdated line</dt>
            <dd>
              {card.github.thread_outdated === null
                ? "Not available"
                : card.github.thread_outdated
                  ? "Marked outdated"
                  : "Not marked outdated"}
            </dd>
          </div>
        </dl>
        <p className="small-copy">
          Reported at capture time. These states do not establish that code is
          correct.
        </p>
      </section>
      <section className="decision-box">
        <div className="section-heading">
          <h3>Your local decision</h3>
          <span className="local-state">
            {decision?.state === "reviewed"
              ? "Reviewed locally"
              : "Not yet reviewed locally"}
          </span>
        </div>
        <label className="field">
          <span>
            Note <span className="optional">(optional)</span>
          </span>
          <textarea
            rows={3}
            maxLength={2000}
            value={note}
            onChange={(event) => {
              setNote(event.target.value);
              onDraft(event.target.value);
              setSaved("");
            }}
            placeholder="What did you conclude after reading the evidence?"
          />
        </label>
        <div className="decision-actions">
          <button
            className="button primary"
            disabled={saving}
            onClick={() =>
              void persist(decision?.state === "reviewed" ? "open" : "reviewed")
            }
          >
            {saving
              ? "Saving…"
              : decision?.state === "reviewed"
                ? "Reopen locally"
                : "Mark reviewed locally"}
            {!saving && (
              <Glyph name={decision?.state === "reviewed" ? "back" : "check"} />
            )}
          </button>
          <button
            className="button"
            disabled={!dirty || saving}
            onClick={() => void persist(decision?.state ?? "open")}
          >
            Save note
          </button>
        </div>
        <p className="small-copy">
          {replay
            ? "Saved only in this browser for this replay."
            : "Saved in this local workspace."}{" "}
          This does not change GitHub.
        </p>
        <p className="save-status" role="status">
          {saved || (dirty ? "Unsaved note" : "")}
        </p>
      </section>
      <details className="conversation-context">
        <summary>
          Read this PR's full conversation{" "}
          <span>{pr.comments.length} source entries</span>
        </summary>
        <SourceTimeline pr={pr} />
      </details>
    </article>
  );
}

function EvidenceQuote({
  title,
  source,
  quote,
  pr,
}: {
  title: string;
  source: SourceComment | undefined;
  quote?: string;
  pr: PullRequest;
}) {
  return (
    <section className={`quote-box ${source ? "" : "absent"}`}>
      <p className="eyebrow">{title}</p>
      {source ? (
        <>
          <div className="quote-author">
            <span className="avatar">
              {source.author.slice(0, 1).toUpperCase() || "?"}
            </span>
            <div>
              <strong>{source.author || "Unknown author"}</strong>
              <small>
                {displayDate(source.created_at)} · {source.kind}
              </small>
              {source.updated_at !== source.created_at && (
                <small>Edited {displayDate(source.updated_at)}</small>
              )}
            </div>
          </div>
          <blockquote>{quote}</blockquote>
          {validSourceUrl(source.url, pr) && (
            <External url={source.url}>Open original on GitHub</External>
          )}
          <details className="full-comment">
            <summary>Show full original comment</summary>
            <pre>{source.body}</pre>
          </details>
        </>
      ) : (
        <>
          <span className="no-response-mark">—</span>
          <p>No relevant later response was identified in this snapshot.</p>
          <p className="small-copy">
            Inspect the conversation before acting. This does not mean no
            response exists.
          </p>
        </>
      )}
    </section>
  );
}
function SourceTimeline({ pr }: { pr: PullRequest }) {
  return (
    <ol className="source-timeline">
      {[...pr.comments]
        .sort(
          (a, b) =>
            Date.parse(a.created_at) - Date.parse(b.created_at) ||
            a.id.localeCompare(b.id),
        )
        .map((comment) => (
          <li key={comment.id}>
            <div className="timeline-meta">
              <strong>{comment.author || "Unknown author"}</strong>
              {comment.is_bot && (
                <span className="bot-label">
                  Automated · excluded from queue
                </span>
              )}
              {comment.author.toLowerCase() === pr.author.toLowerCase() &&
                !comment.is_bot && (
                  <span className="author-label">PR author</span>
                )}
              <span>{comment.kind}</span>
              <time dateTime={comment.created_at}>
                {displayDate(comment.created_at)}
              </time>
            </div>
            {comment.updated_at !== comment.created_at && (
              <p className="small-copy">
                Edited {displayDate(comment.updated_at)}; earlier wording is not
                retained in this snapshot.
              </p>
            )}
            {comment.review_state && (
              <p className="small-copy">
                Review submitted:{" "}
                {comment.review_state.replaceAll("_", " ").toLowerCase()}
              </p>
            )}
            <pre>{comment.body || "(No text in this review submission.)"}</pre>
            {validSourceUrl(comment.url, pr) && (
              <External url={comment.url}>Original source on GitHub</External>
            )}
          </li>
        ))}
    </ol>
  );
}
function Sources({ snapshot }: { snapshot: Snapshot }) {
  const [filter, setFilter] = useState("all");
  return (
    <section className="sources-view">
      <div className="sources-intro">
        <div>
          <h2>The full conversation stays available.</h2>
          <p>
            Original text, review submissions and inline comments, including all
            automated entries. Imported text is untrusted evidence.
          </p>
        </div>
        <label className="field compact">
          Show source type
          <select
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
          >
            <option value="all">All entries</option>
            <option value="bots">Automated entries only</option>
            <option value="human">Human entries only</option>
          </select>
        </label>
      </div>
      {snapshot.prs.map((pr) => {
        const selected = pr.comments.filter(
          (c) => filter === "all" || (filter === "bots" ? c.is_bot : !c.is_bot),
        );
        const counts = {
          comment: pr.comments.filter((c) => c.kind === "comment").length,
          review: pr.comments.filter((c) => c.kind === "review").length,
          inline: pr.comments.filter((c) => c.kind === "inline").length,
        };
        return (
          <section className="source-pr panel" key={pr.id}>
            <header>
              <div>
                <External url={pr.url}>{pr.id}</External>
                <h3>{pr.title}</h3>
                <p>
                  Author: {pr.author} · {pr.state.toLowerCase()} · Captured{" "}
                  {displayDate(pr.fetched_at)}
                </p>
              </div>
              <span
                className={`coverage-label ${pr.complete ? "" : "caution"}`}
              >
                {pr.complete
                  ? "Source intake complete"
                  : "Incomplete source intake"}
              </span>
            </header>
            <div className="source-counts">
              <span>{counts.comment} comments</span>
              <span>{counts.review} review submissions</span>
              <span>{counts.inline} inline entries</span>
              <span>
                {pr.comments.filter((c) => c.is_bot).length} automated
              </span>
            </div>
            {!pr.complete && (
              <Note
                kind="warning"
                title="This PR's source coverage is incomplete"
              >
                <ul>
                  {pr.warnings.map((warning, index) => (
                    <li key={index}>{warning}</li>
                  ))}
                </ul>
              </Note>
            )}
            {selected.length ? (
              <SourceTimeline pr={{ ...pr, comments: selected }} />
            ) : (
              <p className="empty-copy">
                {pr.comments.length
                  ? "No entries match this source filter."
                  : "No discussion entries in this snapshot. This does not establish that no work remains."}
              </p>
            )}
          </section>
        );
      })}
    </section>
  );
}

export default App;
