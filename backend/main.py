import argparse

import uvicorn

from app.core.config import settings
from app.core.logging import setup_logging
from app.factory import create_app

app = create_app()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PubFinder Backend API Server")
    parser.add_argument(
        "--host",
        type=str,
        default=settings.HOST,
        help="Host address to bind the server",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.PORT,
        help="Port to bind the server",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=settings.LOG_LEVEL,
        help="Logging level (DEBUG, INFO, WARNING, ERROR)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging(log_level=args.log_level, json_logs=settings.JSON_LOGS)

    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level.lower(),
    )


if __name__ == "__main__":
    main()
