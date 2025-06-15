from __future__ import annotations

from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database.models import Subscription


class SubscriptionService:
    """Manage VIP channel subscriptions."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_subscription(self, user_id: int, duration_days: int) -> Subscription:
        now = datetime.utcnow()
        sub = await self.session.get(Subscription, user_id)
        if sub:
            if sub.end_date < now:
                sub.start_date = now
                sub.end_date = now + timedelta(days=duration_days)
            else:
                sub.end_date = sub.end_date + timedelta(days=duration_days)
        else:
            sub = Subscription(
                user_id=user_id,
                start_date=now,
                end_date=now + timedelta(days=duration_days),
            )
            self.session.add(sub)
        await self.session.commit()
        await self.session.refresh(sub)
        return sub

    async def get_subscription(self, user_id: int) -> Subscription | None:
        return await self.session.get(Subscription, user_id)

    async def remove_subscription(self, user_id: int) -> None:
        sub = await self.session.get(Subscription, user_id)
        if sub:
            await self.session.delete(sub)
            await self.session.commit()

    async def list_active_subscriptions(self) -> list[Subscription]:
        now = datetime.utcnow()
        stmt = select(Subscription).where(Subscription.end_date > now)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_total_subscriptions(self) -> int:
        stmt = select(func.count()).select_from(Subscription)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def count_expired_subscriptions(self) -> int:
        now = datetime.utcnow()
        stmt = select(func.count()).select_from(Subscription).where(Subscription.end_date <= now)
        result = await self.session.execute(stmt)
        return result.scalar_one()
