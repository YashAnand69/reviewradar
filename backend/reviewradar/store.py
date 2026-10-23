"""Small immutable evidence store; user dispositions are deliberately separate."""

from contextlib import contextmanager
import json
import os
from pathlib import Path
import sqlite3

from .schemas import Analysis, Disposition, Snapshot, utc_now


class Store:
    def __init__(self, data_dir: Path):
        data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = data_dir / "reviewradar.sqlite3"
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id TEXT PRIMARY KEY, fetched_at TEXT NOT NULL,
                    owner TEXT NOT NULL, payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY, snapshot_id TEXT NOT NULL REFERENCES snapshots(id),
                    created_at TEXT NOT NULL, mode TEXT NOT NULL, payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS dispositions (
                    analysis_id TEXT NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
                    card_id TEXT NOT NULL, state TEXT NOT NULL, note TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (analysis_id, card_id)
                );
            """)
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

    def analyses(self) -> list[dict]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT payload FROM analyses ORDER BY created_at DESC, id DESC LIMIT 100"
            ).fetchall()
        return [
            {
                "id": a["id"],
                "snapshot_id": a["snapshot_id"],
                "created_at": a["created_at"],
                "mode": a["mode"],
                "complete": a["complete"],
                "card_count": len(a["cards"]),
                "model": a["model"],
            }
            for a in (json.loads(row["payload"]) for row in rows)
        ]

    def dispositions(self, analysis_id: str) -> list[Disposition]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT * FROM dispositions WHERE analysis_id = ? ORDER BY card_id",
                (analysis_id,),
            ).fetchall()
        return [Disposition.model_validate(dict(row)) for row in rows]

    def set_disposition(
        self, analysis_id: str, card_id: str, state: str, note: str
    ) -> Disposition:
        analysis = self.get_analysis(analysis_id)
        if analysis is None or not any(card.id == card_id for card in analysis.cards):
            raise KeyError("Analysis or card not found")
        disposition = Disposition(
            analysis_id=analysis_id,
            card_id=card_id,
            state=state,
            note=note,
            updated_at=utc_now(),
        )
        with self.connect() as db:
            db.execute(
                """INSERT INTO dispositions VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(analysis_id, card_id) DO UPDATE SET
                state=excluded.state, note=excluded.note, updated_at=excluded.updated_at""",
                (
                    analysis_id,
                    card_id,
                    disposition.state,
                    disposition.note,
                    disposition.updated_at,
                ),
            )
        return disposition
