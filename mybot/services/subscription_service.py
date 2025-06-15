from __future__ import annotations

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database.models import VipSubscription


class SubscriptionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_subscription(self, user_id: int) -> VipSubscription | None:
        stmt = select(VipSubscription).where(VipSubscription.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_subscription(
        self, user_id: int, expires_at: datetime | None = None
    ) -> VipSubscription:
        sub = VipSubscription(user_id=user_id, expires_at=expires_at)
        self.session.add(sub)
        await self.session.commit()
        await self.session.refresh(sub)
        return sub

    async def get_statistics(self) -> tuple[int, int, int]:
        """Return total, active and expired subscription counts."""
        now = datetime.utcnow()

        total_stmt = select(func.count()).select_from(VipSubscription)
        active_stmt = (
            select(func.count())
            .select_from(VipSubscription)
            .where(
                (VipSubscription.expires_at.is_(None))
                | (VipSubscription.expires_at > now)
            )
        )
        expired_stmt = (
            select(func.count())
            .select_from(VipSubscription)
            .where(
                VipSubscription.expires_at.is_not(None),
                VipSubscription.expires_at <= now,
            )
        )

        total_res = await self.session.execute(total_stmt)
        active_res = await self.session.execute(active_stmt)
        expired_res = await self.session.execute(expired_stmt)

        return (
            total_res.scalar() or 0,
            active_res.scalar() or 0,
            expired_res.scalar() or 0,
        )

    async def get_active_subscribers(self) -> list[VipSubscription]:
        """Return list of currently active subscriptions."""
        now = datetime.utcnow()
        stmt = select(VipSubscription).where(
            (VipSubscription.expires_at.is_(None)) | (VipSubscription.expires_at > now)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
