"""Small immutable evidence store; user dispositions are deliberately separate."""

from contextlib import contextmanager
import json
import os
from pathlib import Path
import sqlite3

from .schemas import Analysis, Assessment, Disposition, Snapshot, utc_now


SCHEMA_VERSION = 1


class Store:
    def __init__(self, data_dir: Path):
        data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = data_dir / "reviewradar.sqlite3"
        with self.connect() as db:
            # Keep schema changes and the version marker in one transaction. A
            # write lock also prevents concurrent startups migrating the same DB.
            db.execute("BEGIN IMMEDIATE")
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version > SCHEMA_VERSION:
                raise ValueError(
                    "This database was created by a newer ReviewRadar version. "
                    "Use that version rather than downgrading the database."
                )
            db.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id TEXT PRIMARY KEY, fetched_at TEXT NOT NULL,
                    owner TEXT NOT NULL, payload TEXT NOT NULL
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY, snapshot_id TEXT NOT NULL REFERENCES snapshots(id),
                    created_at TEXT NOT NULL, mode TEXT NOT NULL, payload TEXT NOT NULL
                )
            """)
            db.execute(
                "CREATE INDEX IF NOT EXISTS analyses_created_id "
                "ON analyses(created_at DESC, id DESC)"
            )
            db.execute("""
                CREATE TABLE IF NOT EXISTS dispositions (
                    analysis_id TEXT NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
                    card_id TEXT NOT NULL, state TEXT NOT NULL, note TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (analysis_id, card_id)
                )
            """)
            columns = {
                row["name"] for row in db.execute("PRAGMA table_info(dispositions)")
            }
            if "assessment" not in columns:
                if version == SCHEMA_VERSION:
                    raise ValueError(
                        "The disposition schema is incomplete; restore a consistent database backup."
                    )
                db.execute(
                    "ALTER TABLE dispositions ADD COLUMN assessment TEXT NOT NULL DEFAULT 'unassessed'"
                )
            db.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        os.chmod(self.path, 0o600)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        try:
            with db:
                yield db
        finally:
            db.close()

    def save_snapshot(self, snapshot: Snapshot) -> None:
        payload = snapshot.model_dump_json()
        with self.connect() as db:
            previous = db.execute(
                "SELECT payload FROM snapshots WHERE id = ?", (snapshot.id,)
            ).fetchone()
            if previous is not None:
                if json.loads(previous["payload"]) != json.loads(payload):
                    raise ValueError(
                        "An immutable snapshot ID cannot identify different content"
                    )
                return
            db.execute(
                "INSERT INTO snapshots VALUES (?, ?, ?, ?)",
                (snapshot.id, snapshot.fetched_at, snapshot.owner, payload),
            )

    def get_snapshot(self, snapshot_id: str) -> Snapshot | None:
        with self.connect() as db:
            row = db.execute(
                "SELECT payload FROM snapshots WHERE id = ?", (snapshot_id,)
            ).fetchone()
        return Snapshot.model_validate_json(row["payload"]) if row else None

    def snapshots(self) -> list[dict]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT payload FROM snapshots ORDER BY fetched_at DESC, id DESC LIMIT 100"
            ).fetchall()
        return [
            {
                "id": s["id"],
                "fetched_at": s["fetched_at"],
                "owner": s["owner"],
                "complete": s["complete"],
                "pr_count": len(s["prs"]),
                "source": s["source"],
            }
            for s in (json.loads(row["payload"]) for row in rows)
        ]

    def save_analysis(self, analysis: Analysis) -> None:
        payload = analysis.model_dump_json()
        with self.connect() as db:
            previous = db.execute(
                "SELECT payload FROM analyses WHERE id = ?", (analysis.id,)
            ).fetchone()
            if previous is not None:
                if json.loads(previous["payload"]) != json.loads(payload):
                    raise ValueError(
                        "An immutable analysis ID cannot identify different content"
                    )
                return
            db.execute(
                "INSERT INTO analyses VALUES (?, ?, ?, ?, ?)",
                (
                    analysis.id,
                    analysis.snapshot_id,
                    analysis.created_at,
                    analysis.mode,
                    payload,
                ),
            )

    def get_analysis(self, analysis_id: str) -> Analysis | None:
        with self.connect() as db:
            row = db.execute(
                "SELECT payload FROM analyses WHERE id = ?", (analysis_id,)
            ).fetchone()
        return Analysis.model_validate_json(row["payload"]) if row else None

    def analyses(self, before: str | None = None) -> list[dict]:
        source_prs: dict[str, list[dict]] = {}
        with self.connect() as db:
            # Resolve the cursor and its page in one read transaction. Newer
            # analyses can be inserted between pages without shifting older rows.
            db.execute("BEGIN")
            values: tuple = ()
            where = ""
            if before is not None:
                cursor = db.execute(
                    "SELECT created_at, id FROM analyses WHERE id = ?", (before,)
                ).fetchone()
                if cursor is None:
                    raise KeyError("History cursor not found")
                where = "WHERE (a.created_at, a.id) < (?, ?)"
                values = (cursor["created_at"], cursor["id"])
            rows = db.execute(
                f"""SELECT a.payload, s.owner, s.fetched_at,
                    s.id AS source_id
                    FROM analyses a JOIN snapshots s ON s.id = a.snapshot_id
                    {where}
                    ORDER BY a.created_at DESC, a.id DESC LIMIT 100""",
                values,
            ).fetchall()
            # Several readings may share a large discussion snapshot. Read each
            # source once rather than duplicating its full body for every row.
            source_ids = list(dict.fromkeys(row["source_id"] for row in rows))
            if source_ids:
                placeholders = ",".join("?" for _ in source_ids)
                for source in db.execute(
                    f"SELECT id, payload FROM snapshots WHERE id IN ({placeholders})",
                    source_ids,
                ):
                    source_prs[source["id"]] = [
                        {key: pr[key] for key in ("id", "title", "url")}
                        for pr in json.loads(source["payload"])["prs"]
                    ]
        result = []
        for row in rows:
            analysis = json.loads(row["payload"])
            source_id = row["source_id"]
            result.append(
                {
                    "id": analysis["id"],
                    "snapshot_id": analysis["snapshot_id"],
                    "created_at": analysis["created_at"],
                    "mode": analysis["mode"],
                    "complete": analysis["complete"],
                    "card_count": len(analysis["cards"]),
                    "model": analysis["model"],
                    "owner": row["owner"],
                    "fetched_at": row["fetched_at"],
                    "prs": source_prs[source_id],
                }
            )
        return result

    def dispositions(self, analysis_id: str) -> list[Disposition]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT * FROM dispositions WHERE analysis_id = ? ORDER BY card_id",
                (analysis_id,),
            ).fetchall()
        return [Disposition.model_validate(dict(row)) for row in rows]

    def set_disposition(
        self,
        analysis_id: str,
        card_id: str,
        state: str,
        note: str,
        assessment: Assessment | None = None,
    ) -> Disposition:
        analysis = self.get_analysis(analysis_id)
        if analysis is None:
            raise KeyError("Analysis or card not found")
        card = next((card for card in analysis.cards if card.id == card_id), None)
        if card is None:
            raise KeyError("Analysis or card not found")
        if assessment is not None and assessment != "unassessed":
            if analysis.mode != "model":
                raise ValueError(
                    "Model assessments apply only to model analyses, not the chronology baseline."
                )
            if assessment == "reply_not_relevant" and card.response is None:
                raise ValueError(
                    "A reply can be assessed only when the card has a possible response."
                )
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            previous = db.execute(
                "SELECT assessment FROM dispositions WHERE analysis_id = ? AND card_id = ?",
                (analysis_id, card_id),
            ).fetchone()
            saved_assessment = previous["assessment"] if previous else "unassessed"
            disposition = Disposition(
                analysis_id=analysis_id,
                card_id=card_id,
                state=state,
                note=note,
                assessment=assessment if assessment is not None else saved_assessment,
                updated_at=utc_now(),
            )
            db.execute(
                """INSERT INTO dispositions (analysis_id, card_id, state, note, updated_at, assessment)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(analysis_id, card_id) DO UPDATE SET
                state=excluded.state, note=excluded.note, updated_at=excluded.updated_at,
                assessment=excluded.assessment""",
                (
                    analysis_id,
                    card_id,
                    disposition.state,
                    disposition.note,
                    disposition.updated_at,
                    disposition.assessment,
                ),
            )
        return disposition
