from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import ConfigEntry
from utils.text_utils import sanitize_text


class ConfigService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_value(self, key: str) -> str | None:
        entry = await self.session.get(ConfigEntry, key)
        return entry.value if entry else None

    async def set_value(self, key: str, value: str) -> ConfigEntry:
        """Store a configuration value, sanitizing text to avoid encoding issues."""
        clean_value = sanitize_text(value)
        entry = await self.session.get(ConfigEntry, key)
        if entry:
            entry.value = clean_value
        else:
            entry = ConfigEntry(key=key, value=clean_value)
            self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry

