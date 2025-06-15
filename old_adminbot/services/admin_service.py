from __future__ import annotations

from database import get_db

__all__ = ["ensure_admins"]


async def ensure_admins(admin_ids: list[int]) -> None:
    """Insert or update admin users in the database."""
    if not admin_ids:
        return
    db = get_db()
    for admin_id in admin_ids:
        await db.execute(
            "INSERT OR IGNORE INTO user (id, username, full_name) VALUES (?, ?, ?)",
            (admin_id, str(admin_id), str(admin_id)),
        )
        await db.execute("UPDATE user SET is_admin=1 WHERE id=?", (admin_id,))
    await db.commit()

