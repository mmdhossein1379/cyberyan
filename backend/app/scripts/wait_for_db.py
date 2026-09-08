from __future__ import annotations

import asyncio
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


async def wait_for_database(max_attempts: int = 60, delay_seconds: float = 2.0) -> None:
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)

    try:
        for attempt in range(1, max_attempts + 1):
            try:
                async with engine.connect() as connection:
                    await connection.execute(text("SELECT 1"))
                print("Database is ready.", flush=True)
                return
            except Exception as exc:  # startup diagnostic/retry path
                print(
                    f"Database not ready ({attempt}/{max_attempts}): "
                    f"{exc.__class__.__name__}: {exc}",
                    flush=True,
                )
                if attempt < max_attempts:
                    await asyncio.sleep(delay_seconds)
    finally:
        await engine.dispose()

    raise RuntimeError("Database did not become available before startup timeout.")


def main() -> None:
    try:
        asyncio.run(wait_for_database())
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"Database startup check failed: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
