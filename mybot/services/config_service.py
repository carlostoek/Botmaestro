from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import ConfigEntry
from utils.text_utils import sanitize_text


class ConfigService:
    VIP_CHANNEL_KEY = "VIP_CHANNEL_ID"
    FREE_CHANNEL_KEY = "FREE_CHANNEL_ID"
    REACTION_BUTTONS_KEY = "reaction_buttons"

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

    async def get_vip_channel_id(self) -> int | None:
        value = await self.get_value(self.VIP_CHANNEL_KEY)
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    async def set_vip_channel_id(self, chat_id: int) -> ConfigEntry:
        return await self.set_value(self.VIP_CHANNEL_KEY, str(chat_id))

    async def get_free_channel_id(self) -> int | None:
        value = await self.get_value(self.FREE_CHANNEL_KEY)
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    async def set_free_channel_id(self, chat_id: int) -> ConfigEntry:
        return await self.set_value(self.FREE_CHANNEL_KEY, str(chat_id))

    async def get_reaction_buttons(self) -> list[str]:
        """Return custom reaction button texts or defaults."""
        value = await self.get_value(self.REACTION_BUTTONS_KEY)
        if value:
            texts = [t.strip() for t in value.split(";") if t.strip()]
            if texts:
                return texts[:10]
        from utils.config import DEFAULT_REACTION_BUTTONS

        return DEFAULT_REACTION_BUTTONS

