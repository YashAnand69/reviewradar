"""Start only this project's loopback app."""

import uvicorn

from .app import create_app
from .config import Settings


def main():
    settings = Settings()
    uvicorn.run(
        create_app(settings),
        host="127.0.0.1",
        port=settings.port,
        access_log=False,
        proxy_headers=False,
    )


if __name__ == "__main__":
    main()
