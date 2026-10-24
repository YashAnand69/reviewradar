export interface SourceComment {
  id: string;
  url: string;
  author: string;
  is_bot: boolean;
  kind: "comment" | "review" | "inline";
  body: string;
  created_at: string;
  updated_at: string;
  review_state: string | null;
  thread_id: string | null;
  thread_resolved: boolean | null;
  thread_outdated: boolean | null;
}
export interface PullRequest {
  id: string;
  url: string;
  title: string;
  author: string;
  state: "OPEN" | "CLOSED" | "MERGED";
  head_sha: string | null;
  fetched_at: string;
  complete: boolean;
  warnings: string[];
  comments: SourceComment[];
}
export interface Snapshot {
  schema_version: 1;
  id: string;
  fetched_at: string;
  source: "github" | "import" | "synthetic";
  owner: string;
  prs: PullRequest[];
  complete: boolean;
  warnings: string[];
}
export interface Card {
  id: string;
  pr_id: string;
  request: { comment_id: string; quote: string };
  response: { comment_id: string; quote: string } | null;
  category: "change" | "question" | "suggestion" | "unclear";
  interpretation: "follow_up" | "possibly_responded" | "unclear";
  rationale: string;
  uncertainty: string[];
  github: {
    review_state: string | null;
    thread_resolved: boolean | null;
    thread_outdated: boolean | null;
  };
}
export interface Coverage {
  pr_id: string;
  status: "analyzed" | "failed" | "rejected_oversize";
  comments_total: number;
  comments_processed: number;
  comments_excluded_bots: number;
  reason: string | null;
}
export interface Analysis {
  id: string;
  snapshot_id: string;
  mode: "model" | "baseline";
  scope: "human_review";
  model: string | null;
  prompt_version: string;
  created_at: string;
  complete: boolean;
  warnings: string[];
  cards: Card[];
  coverage: Coverage[];
  stats: {
    comments_total: number;
    comments_processed: number;
    comments_excluded_bots: number;
    elapsed_seconds: number;
  };
}
export type Assessment = "unassessed" | "not_a_request" | "reply_not_relevant";
export interface Disposition {
  analysis_id: string;
  card_id: string;
  state: "open" | "reviewed";
  note: string;
  // Older saved replay decisions have no assessment.
  assessment?: Assessment;
  updated_at: string;
}
export interface Health {
  status: string;
  version: string;
  model_configured: boolean;
  model_ready?: boolean;
  model_reason?: string | null;
  github_available: boolean;
  mode: "local";
}
export interface SavedAnalysis {
  id: string;
  snapshot_id: string;
  created_at: string;
  mode: string;
  complete?: boolean;
  cards_count?: number;
  model?: string | null;
}
export interface Sample {
  snapshot: Snapshot;
  analysis?: Analysis;
  manifest?: Record<string, unknown>;
}
export type SavedExample = "original" | "mixed";
