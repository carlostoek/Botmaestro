from __future__ import annotations

from datetime import datetime, timedelta
from secrets import token_urlsafe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import InviteToken, SubscriptionToken, Token


class TokenService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_token(self, created_by: int, expires_in: int | None = None) -> InviteToken:
        token = token_urlsafe(16)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in) if expires_in else None
        obj = InviteToken(token=token, created_by=created_by, expires_at=expires_at)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def use_token(self, token: str, user_id: int) -> bool:
        stmt = select(InviteToken).where(InviteToken.token == token)
        result = await self.session.execute(stmt)
        obj = result.scalar_one_or_none()
        if not obj or obj.used_by or (obj.expires_at and obj.expires_at < datetime.utcnow()):
            return False
        obj.used_by = user_id
        obj.used_at = datetime.utcnow()
        await self.session.commit()
        return True

    async def create_subscription_token(self, plan_id: int, created_by: int) -> SubscriptionToken:
        token = token_urlsafe(8)
        obj = SubscriptionToken(token=token, plan_id=plan_id, created_by=created_by)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def redeem_subscription_token(self, token: str, user_id: int) -> SubscriptionToken | None:
        stmt = select(SubscriptionToken).where(SubscriptionToken.token == token)
        result = await self.session.execute(stmt)
        obj = result.scalar_one_or_none()
        if not obj or obj.used_by:
            return None
        obj.used_by = user_id
        obj.used_at = datetime.utcnow()
        await self.session.commit()
        return obj


async def validate_token(token: str, session: AsyncSession) -> str | None:
    """Validate a VIP activation token and mark it as used."""

    stmt = select(Token).where(Token.token_id == token)
    result = await session.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj or obj.is_used:
        return None
    obj.is_used = True
    await session.commit()
    return obj.subscription_duration

