from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import Channel


class ChannelService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_channel(self, chat_id: int, title: str | None = None) -> Channel:
        channel = await self.session.get(Channel, chat_id)
        if channel:
            if title:
                channel.title = title
        else:
            channel = Channel(id=chat_id, title=title)
            self.session.add(channel)
        await self.session.commit()
        await self.session.refresh(channel)
        return channel

    async def list_channels(self) -> list[Channel]:
        result = await self.session.execute(select(Channel))
        return list(result.scalars().all())

    async def remove_channel(self, chat_id: int) -> None:
        channel = await self.session.get(Channel, chat_id)
        if channel:
            await self.session.delete(channel)
            await self.session.commit()
