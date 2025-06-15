import aiosqlite
from pathlib import Path

from .models import SCHEMA

_db: aiosqlite.Connection | None = None


async def init_db(path: str = "db.sqlite3") -> aiosqlite.Connection:
    """Initialize the SQLite database and return the connection."""
    global _db
    if _db is None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        _db = await aiosqlite.connect(path)
        _db.row_factory = aiosqlite.Row
        await _db.executescript(SCHEMA)
        await _db.commit()
    return _db


def get_db() -> aiosqlite.Connection:
    """Return the initialized database connection."""
    if _db is None:
        raise RuntimeError("Database not initialized")
    return _db
