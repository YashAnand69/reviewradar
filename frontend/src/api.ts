import type {
  Analysis,
  Assessment,
  Disposition,
  Health,
  Sample,
  SavedAnalysis,
  SavedExample,
  Snapshot,
} from "./types";
let sessionToken = "";
let refreshPending: Promise<void> | null = null;

const connectionMessage =
  "The local ReviewRadar server is not responding. Your open evidence and typed notes remain in this tab. Double-click Start ReviewRadar.command in the project folder, keep its Terminal open, then choose Retry connection; do not reload before saving your notes.";

export class LocalConnectionError extends Error {
  constructor(message = connectionMessage) {
    super(message);
    this.name = "LocalConnectionError";
  }
}

async function localFetch(path: string, init: RequestInit = {}) {
  try {
    return await fetch(path, init);
  } catch {
    throw new LocalConnectionError();
  }
}

async function refreshSession() {
  if (!refreshPending) {
    refreshPending = (async () => {
      const response = await localFetch("/runtime-config", {
        cache: "no-store",
        signal: AbortSignal.timeout(5000),
      });
      if (!response.ok)
        throw new LocalConnectionError(
          "The local server could not open a session. Start ReviewRadar, then choose Retry connection. Your open evidence and typed notes remain in this tab.",
        );
      let data: unknown;
      try {
        data = await response.json();
      } catch {
        throw new LocalConnectionError(
          "The local application configuration is invalid. Restart ReviewRadar and retry the connection.",
        );
      }
      if (
        !data ||
        typeof data !== "object" ||
        !("api_token" in data) ||
        typeof data.api_token !== "string" ||
        !data.api_token
      )
        throw new LocalConnectionError(
          "The local application configuration is invalid. Restart ReviewRadar and retry the connection.",
        );
      sessionToken = data.api_token;
    })().finally(() => {
      refreshPending = null;
    });
  }
  return refreshPending;
}

async function responseFor(
  path: string,
  init: RequestInit = {},
): Promise<Response> {
  async function send() {
    return localFetch(path, {
      ...init,
      headers: {
        "X-ReviewRadar-Token": sessionToken,
        ...(init.body ? { "Content-Type": "application/json" } : {}),
        ...init.headers,
      },
    });
  }
  const usedToken = sessionToken;
  let response = await send();
  // A 401 rejects the request before execution. Renew only this session and
  // retry once; network errors and other failures may follow an executed write.
  if (response.status === 401) {
    if (usedToken === sessionToken) await refreshSession();
    response = await send();
    if (response.status === 401)
      throw new LocalConnectionError(
        "Your local session could not be renewed. Choose Retry connection. Your open evidence and typed notes remain in this tab.",
      );
  }
  if (!response.ok) {
    let message = `Request failed (${response.status}).`;
    try {
      const data = await response.json();
      message = typeof data.detail === "string" ? data.detail : message;
    } catch {
      /* Preserve the status when the server has no JSON error body. */
    }
    throw new Error(message);
  }
  return response;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  return (await responseFor(path, init)).json();
}
export const api = {
  async connect(): Promise<Health> {
    await refreshSession();
    return api.health();
  },
  async health(): Promise<Health> {
    try {
      return await request<Health>("/api/health", {
        signal: AbortSignal.timeout(5000),
      });
    } catch (cause) {
      if (cause instanceof LocalConnectionError) throw cause;
      throw new LocalConnectionError(
        "The local workspace is not ready. Start ReviewRadar, then choose Retry connection. Your open evidence and typed notes remain in this tab.",
      );
    }
  },
  sample: (example: SavedExample = "original") => {
    if (example !== "original" && example !== "mixed")
      throw new Error("Choose one of the published saved examples.");
    return request<Sample | Snapshot>(
      example === "mixed" ? "/api/sample?example=mixed" : "/api/sample",
    );
  },
  history: (before?: string) =>
    request<SavedAnalysis[]>(
      before ? `/api/analyses?before=${encodeURIComponent(before)}` : "/api/analyses",
    ),
  snapshot: (id: string) =>
    request<Snapshot>(`/api/snapshots/${encodeURIComponent(id)}`),
  analysis: (id: string) =>
    request<Analysis>(`/api/analyses/${encodeURIComponent(id)}`),
  dispositions: (id: string) =>
    request<Disposition[]>(
      `/api/analyses/${encodeURIComponent(id)}/dispositions`,
    ),
  importSnapshot: (snapshot: unknown) =>
    request<Snapshot>("/api/snapshots/import", {
      method: "POST",
      body: JSON.stringify({ snapshot }),
    }),
  importGithub: (owner: string, urls: string[]) =>
    request<Snapshot>("/api/snapshots/github", {
      method: "POST",
      body: JSON.stringify({ owner, urls }),
    }),
  analyse: (snapshot_id: string, mode: "model" | "baseline") =>
    request<Analysis>("/api/analyses", {
      method: "POST",
      body: JSON.stringify({ snapshot_id, mode }),
    }),
  save: (
    analysisId: string,
    cardId: string,
    state: "open" | "reviewed",
    note: string,
    assessment?: Assessment,
  ) =>
    request<Disposition>(
      `/api/analyses/${encodeURIComponent(analysisId)}/cards/${encodeURIComponent(cardId)}/disposition`,
      { method: "PUT", body: JSON.stringify({ state, note, assessment }) },
    ),
  async export(id: string): Promise<Blob> {
    const response = await responseFor(
      `/api/analyses/${encodeURIComponent(id)}/export`,
    );
    return response.blob();
  },
};
