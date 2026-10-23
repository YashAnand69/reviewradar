"""Explicit, local-only configuration. No credentials are returned to the UI."""

from dataclasses import dataclass, field
import os
from pathlib import Path
import secrets
from urllib.parse import urlsplit


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAX_BODY_BYTES = 2 * 1024 * 1024
MAX_PRS = 5
MAX_COMMENTS = 200
MAX_COMMENT_CHARS = 20_000
MAX_QUOTE_CHARS = 600


@dataclass(frozen=True)
class Settings:
    root: Path = PROJECT_ROOT
    data_dir: Path = field(
        default_factory=lambda: Path(
            os.environ.get("RR_DATA_DIR", str(PROJECT_ROOT / ".data"))
        )
    )
    port: int = field(default_factory=lambda: int(os.environ.get("RR_PORT", "8893")))
    api_token: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    model_url: str = field(
        default_factory=lambda: os.environ.get("RR_MODEL_URL", "http://127.0.0.1:18085")
    )
    model_key_file: Path = field(
        default_factory=lambda: Path(
            os.environ.get(
                "RR_MODEL_KEY_FILE", str(PROJECT_ROOT / ".runtime/model.key")
            )
        )
    )
    model_name: str = field(
        default_factory=lambda: os.environ.get(
            "RR_MODEL_NAME", "reviewradar-gemma4-e2b"
        )
    )
    model_context: int = field(
        default_factory=lambda: int(os.environ.get("RR_MODEL_CONTEXT", "16384"))
    )
    model_output: int = 2048
    model_margin: int = 1024
    model_timeout: float = 90.0

    def __post_init__(self) -> None:
        parsed = urlsplit(self.model_url)
        if (
            parsed.scheme != "http"
            or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
            or parsed.username
            or parsed.password
            or parsed.path not in {"", "/"}
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError(
                "RR_MODEL_URL must be an HTTP loopback origin without credentials or a path"
            )
        if self.model_context <= self.model_output + self.model_margin:
            raise ValueError("Model context must exceed output and safety reserves")
        if not 1024 <= self.port <= 65535:
            raise ValueError("RR_PORT must be between 1024 and 65535")
        if len(self.api_token) < 24:
            raise ValueError("App session token must contain at least 24 characters")

    @property
    def origins(self) -> set[str]:
        return {f"http://127.0.0.1:{self.port}", f"http://localhost:{self.port}"}

    @property
    def hosts(self) -> set[str]:
        return {f"127.0.0.1:{self.port}", f"localhost:{self.port}"}

    @property
    def sample_file(self) -> Path:
        return self.root / "frontend/public/sample.json"

    @property
    def frontend_dir(self) -> Path:
        return self.root / "frontend/dist"

    @property
    def model_configured(self) -> bool:
        return self.model_key_file.is_file()
