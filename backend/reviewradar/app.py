"""Same-origin local API and built interface. No GitHub write routes exist."""

import json
import secrets
import shutil
import threading
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import ValidationError
from starlette.staticfiles import StaticFiles

from . import __version__
from .analysis import export_markdown, run_analysis, validate_bound_analysis
from .config import MAX_BODY_BYTES, Settings
from .model import LocalModel, ModelFailure
from .schemas import (
    Analysis,
    AnalysisRequest,
    DispositionRequest,
    GitHubRequest,
    ImportRequest,
    normalize_snapshot,
)
from .store import Store


class LocalBoundary:
    """Reject hostile hosts/origins before body parsing; bound every request body."""

    def __init__(self, app, settings: Settings):
        self.app, self.settings = app, settings

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        pairs = scope.get("headers", [])
        headers = {key.lower(): value for key, value in pairs}
        path, method = scope.get("path", ""), scope["method"]

        async def reject(status: int, detail: str):
            await JSONResponse(
                {"detail": detail},
                status_code=status,
                headers={
                    "Cache-Control": "no-store",
                    "X-Content-Type-Options": "nosniff",
                },
            )(scope, receive, send)

        host_headers = [value for key, value in pairs if key.lower() == b"host"]
        if (
            len(host_headers) != 1
            or host_headers[0].decode("latin-1").lower() not in self.settings.hosts
        ):
            await reject(400, "Only the configured loopback app origin is accepted.")
            return
        origin = headers.get(b"origin", b"").decode("latin-1")
        if origin and origin not in self.settings.origins:
            await reject(403, "Cross-origin access is not allowed.")
            return
        if headers.get(b"sec-fetch-site", b"") == b"cross-site":
            await reject(403, "Cross-site access is not allowed.")
            return
        if path.startswith("/api/") and path != "/api/health":
            token = headers.get(b"x-reviewradar-token", b"").decode("latin-1")
            if not secrets.compare_digest(token, self.settings.api_token):
                await reject(
                    401,
                    "The local app session is missing or expired. Reload this page.",
                )
                return
        if method not in {"GET", "HEAD", "OPTIONS"}:
            if origin not in self.settings.origins:
                await reject(403, "A matching local Origin is required for changes.")
                return
            if (
                headers.get(b"content-type", b"").split(b";", 1)[0].strip().lower()
                != b"application/json"
            ):
                await reject(415, "Send JSON using application/json.")
                return
        content_length = headers.get(b"content-length")
        if content_length:
            try:
                if int(content_length) < 0 or int(content_length) > MAX_BODY_BYTES:
                    raise ValueError
            except ValueError:
                await reject(413, "Request exceeds the 2 MiB size limit.")
                return
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            body.extend(message.get("body", b""))
            if len(body) > MAX_BODY_BYTES:
                await reject(413, "Request exceeds the 2 MiB size limit.")
                return
            if not message.get("more_body", False):
                break
        received = False

        async def replay():
            nonlocal received
            if not received:
                received = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        async def secure_send(message):
            if message["type"] == "http.response.start":
                response_headers = list(message.get("headers", []))
                response_headers.extend(
                    [
                        (b"x-content-type-options", b"nosniff"),
                        (b"x-frame-options", b"DENY"),
                        (b"referrer-policy", b"no-referrer"),
                        (
                            b"content-security-policy",
                            b"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
                        ),
                    ]
                )
                if path.startswith("/api/") or path == "/runtime-config":
                    response_headers.append((b"cache-control", b"no-store"))
                message["headers"] = response_headers
            await send(message)

        await self.app(scope, replay, secure_send)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    store = Store(settings.data_dir)
    app = FastAPI(
        title="ReviewRadar",
        version=__version__,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.settings, app.state.store = settings, store
    app.state.operation_lock = threading.Lock()
    app.add_middleware(LocalBoundary, settings=settings)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(_request, _exc):
        return JSONResponse(
            {
                "detail": "Request did not match the expected format. Check fields, types and documented limits."
            },
            status_code=422,
        )

    @app.get("/runtime-config")
    def runtime_config():
        return {"api_token": settings.api_token, "mode": "local"}

    @app.get("/api/health")
    def health():
        model = LocalModel(settings).readiness()
        return {
            "status": "ok",
            "version": __version__,
            "model_configured": settings.model_configured,
            "model_ready": model["ready"],
            "model_reason": model["reason"],
            "github_available": shutil.which("gh") is not None,
            "mode": "local",
        }

    @app.get("/api/snapshots")
    def snapshots():
        return store.snapshots()

    @app.get("/api/snapshots/{snapshot_id}")
    def snapshot(snapshot_id: str):
        result = store.get_snapshot(snapshot_id)
        if result is None:
            raise HTTPException(404, "Snapshot not found.")
        return result

    @app.post("/api/snapshots/import")
    def import_snapshot(request: ImportRequest):
        try:
            result = normalize_snapshot(request.snapshot, source="import")
        except (ValidationError, ValueError) as exc:
            raise HTTPException(
                422,
                "Snapshot validation failed. Check its schema, owner, dates, source URLs and documented size limits.",
            ) from exc
        store.save_snapshot(result)
        return result

    @app.post("/api/snapshots/github")
    def github_snapshot(request: GitHubRequest):
        if not app.state.operation_lock.acquire(blocking=False):
            raise HTTPException(
                409, "An import or analysis is already running. Wait for it to finish."
            )
        try:
            from .github import fetch_github_snapshot

            try:
                result = normalize_snapshot(
                    fetch_github_snapshot(request.urls, request.owner), source="github"
                )
            except (ValueError, ValidationError) as exc:
                detail = (
                    "GitHub returned evidence outside the supported schema. Retry with a smaller selection."
                    if isinstance(exc, ValidationError)
                    else str(exc)
                )
                raise HTTPException(422, detail) from exc
            store.save_snapshot(result)
            return result
        finally:
            app.state.operation_lock.release()

    @app.post("/api/analyses")
    def analyze(request: AnalysisRequest):
        snapshot = store.get_snapshot(request.snapshot_id)
        if snapshot is None:
            raise HTTPException(404, "Snapshot not found.")
        if not app.state.operation_lock.acquire(blocking=False):
            raise HTTPException(
                409, "An import or analysis is already running. Wait for it to finish."
            )
        try:
            result = run_analysis(snapshot, request.mode, settings)
            validate_bound_analysis(result, snapshot)
            store.save_analysis(result)
            return result
        finally:
            app.state.operation_lock.release()

    @app.get("/api/analyses")
    def analyses():
        return store.analyses()

    def get_analysis(analysis_id: str):
        result = store.get_analysis(analysis_id)
        if result is None:
            raise HTTPException(404, "Analysis not found.")
        return result

    @app.get("/api/analyses/{analysis_id}")
    def analysis(analysis_id: str):
        return get_analysis(analysis_id)

    @app.get("/api/analyses/{analysis_id}/export")
    def export(analysis_id: str):
        analysis = get_analysis(analysis_id)
        snapshot = store.get_snapshot(analysis.snapshot_id)
        if snapshot is None:
            raise HTTPException(404, "The source snapshot is unavailable.")
        result = export_markdown(analysis, snapshot, store.dispositions(analysis_id))
        return Response(
            result,
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="reviewradar-inspection.md"'
            },
        )

    @app.get("/api/analyses/{analysis_id}/dispositions")
    def dispositions(analysis_id: str):
        get_analysis(analysis_id)
        return store.dispositions(analysis_id)

    @app.put("/api/analyses/{analysis_id}/cards/{card_id}/disposition")
    def disposition(analysis_id: str, card_id: str, request: DispositionRequest):
        try:
            return store.set_disposition(
                analysis_id,
                card_id,
                request.state,
                request.note,
                request.assessment
                if "assessment" in request.model_fields_set
                else None,
            )
        except KeyError as exc:
            raise HTTPException(404, "Analysis or card not found.") from exc
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.get("/api/sample")
    def sample(example: Literal["original", "mixed"] = "original"):
        try:
            path = (
                settings.sample_file
                if example == "original"
                else settings.sample_file.with_name("mixed-sample.json")
            )
            raw = json.loads(path.read_text())
            snapshot = normalize_snapshot(raw["snapshot"])
            analysis = (
                Analysis.model_validate(raw["analysis"])
                if raw.get("analysis") is not None
                else None
            )
            if analysis:
                validate_bound_analysis(analysis, snapshot)
            store.save_snapshot(snapshot)
            if analysis:
                store.save_analysis(analysis)
            return {
                "snapshot": snapshot,
                "analysis": analysis,
                "manifest": raw.get("manifest", {}),
            }
        except (OSError, ValueError, KeyError, ValidationError, ModelFailure) as exc:
            raise HTTPException(
                503,
                "The bundled historical sample is unavailable or failed validation. You can import a public PR or a snapshot instead.",
            ) from exc

    assets = settings.frontend_dir / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{path:path}")
    def frontend(path: str):
        if path.startswith("api/") or path == "runtime-config":
            raise HTTPException(404, "Route not found.")
        if (
            path
            and "/" not in path
            and path
            in {"sample.json", "trial.html", "favicon.svg", "manifest.webmanifest"}
        ):
            target = settings.frontend_dir / path
            if target.is_file():
                return FileResponse(target)
        index = settings.frontend_dir / "index.html"
        if index.is_file():
            return FileResponse(index, headers={"Cache-Control": "no-cache"})
        raise HTTPException(
            503,
            "Build the frontend before opening the local app. API health is available at /api/health.",
        )

    return app
