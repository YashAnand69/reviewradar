import type {
  Analysis,
  Disposition,
  Health,
  Sample,
  SavedAnalysis,
  Snapshot,
} from "./types";
let sessionToken = "";
async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      "X-ReviewRadar-Token": sessionToken,
      ...(init.body ? { "Content-Type": "application/json" } : {}),
      ...init.headers,
    },
  });
  if (!response.ok) {
    let message = `Request failed (${response.status}).`;
    try {
      const data = await response.json();
      message = typeof data.detail === "string" ? data.detail : message;
    } catch {
      /* Safe generic error. */
    }
    throw new Error(message);
  }
  return response.json();
}
export const api = {
  async connect(): Promise<Health> {
    const config = await fetch("/runtime-config", { cache: "no-store" });
    if (!config.ok)
      throw new Error(
        "The local backend could not be reached. Start ReviewRadar using the documented local command.",
      );
    const data = await config.json();
    if (typeof data.api_token !== "string")
      throw new Error("The local application configuration is invalid.");
    sessionToken = data.api_token;
    return request<Health>("/api/health");
  },
  sample: () => request<Sample | Snapshot>("/api/sample"),
  history: () => request<SavedAnalysis[]>("/api/analyses"),
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
  ) =>
    request<Disposition>(
      `/api/analyses/${encodeURIComponent(analysisId)}/cards/${encodeURIComponent(cardId)}/disposition`,
      { method: "PUT", body: JSON.stringify({ state, note }) },
    ),
  async export(id: string): Promise<Blob> {
    const response = await fetch(
      `/api/analyses/${encodeURIComponent(id)}/export`,
      { headers: { "X-ReviewRadar-Token": sessionToken } },
    );
    if (!response.ok)
      throw new Error(
        "The export could not be created. Retry after checking the local backend.",
      );
    return response.blob();
  },
};
