from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import ConfigEntry


class ConfigService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_value(self, key: str) -> str | None:
        entry = await self.session.get(ConfigEntry, key)
        return entry.value if entry else None

    async def set_value(self, key: str, value: str) -> ConfigEntry:
        entry = await self.session.get(ConfigEntry, key)
        if entry:
            entry.value = value
        else:
            entry = ConfigEntry(key=key, value=value)
            self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry

