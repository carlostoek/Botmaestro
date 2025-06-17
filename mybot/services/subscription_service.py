from __future__ import annotations

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database.models import VipSubscription, User, Token, Tariff
from utils.user_roles import VIP_ROLE, FREE_ROLE


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

    async def extend_subscription(self, user_id: int, days: int) -> VipSubscription:
        """Extend an existing subscription or create one if missing."""
        from datetime import timedelta

        now = datetime.utcnow()
        sub = await self.get_subscription(user_id)
        new_exp = now + timedelta(days=days)
        if sub:
            if sub.expires_at and sub.expires_at > now:
                sub.expires_at = sub.expires_at + timedelta(days=days)
            else:
                sub.expires_at = new_exp
        else:
            sub = VipSubscription(user_id=user_id, expires_at=new_exp)
            self.session.add(sub)

        user = await self.session.get(User, user_id)
        if user:
            user.role = VIP_ROLE
            if user.vip_expires_at and user.vip_expires_at > now:
                user.vip_expires_at = user.vip_expires_at + timedelta(days=days)
            else:
                user.vip_expires_at = new_exp
            user.last_reminder_sent_at = None

        await self.session.commit()
        return sub

    async def revoke_subscription(self, user_id: int) -> None:
        """Immediately expire a user's subscription."""
        now = datetime.utcnow()
        sub = await self.get_subscription(user_id)
        if sub:
            sub.expires_at = now

        user = await self.session.get(User, user_id)
        if user:
            user.role = FREE_ROLE
            user.vip_expires_at = None

        await self.session.commit()


async def get_admin_statistics(session: AsyncSession) -> dict:
    """Return statistics for the admin panel."""

    sub_service = SubscriptionService(session)
    total_subs, active_subs, expired_subs = await sub_service.get_statistics()

    user_count_stmt = select(func.count()).select_from(User)
    user_count_res = await session.execute(user_count_stmt)
    total_users = user_count_res.scalar() or 0

    revenue_stmt = (
        select(func.sum(Tariff.price))
        .select_from(Token)
        .join(Tariff, Token.tariff_id == Tariff.id)
        .where(Token.is_used.is_(True))
    )
    revenue_res = await session.execute(revenue_stmt)
    total_revenue = revenue_res.scalar() or 0

    return {
        "subscriptions_total": total_subs,
        "subscriptions_active": active_subs,
        "subscriptions_expired": expired_subs,
        "users_total": total_users,
        "revenue_total": total_revenue,
    }
