from __future__ import annotations

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import VipSubscription


class SubscriptionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_subscription(self, user_id: int) -> VipSubscription | None:
        stmt = select(VipSubscription).where(VipSubscription.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_subscription(self, user_id: int, expires_at: datetime | None = None) -> VipSubscription:
        sub = VipSubscription(user_id=user_id, expires_at=expires_at)
        self.session.add(sub)
        await self.session.commit()
        await self.session.refresh(sub)
        return sub

