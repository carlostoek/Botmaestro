from __future__ import annotations

import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import Token, SubscriptionPlan


class TokenService:
    """Generate and validate invitation tokens."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def generate_token(self, duration_days: int, name: str = "", price: int = 0) -> str:
        """Backward compatible helper used to create a simple token."""
        token = await self.create_token_for_plan(
            (await self.add_subscription_plan(duration_days, name or "plan", price)).id
        )
        return token.token
    async def add_subscription_plan(self, duration_days: int, name: str, price: int) -> SubscriptionPlan:
        """Create and store a subscription plan."""
        plan = SubscriptionPlan(duration_days=duration_days, name=name, price=price)
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        return plan

    async def get_plans(self) -> list[SubscriptionPlan]:
        result = await self.session.execute(select(SubscriptionPlan))
        return result.scalars().all()

    async def create_token_for_plan(self, plan_id: int) -> Token:
        """Generate a token linked to a subscription plan."""
        plan = await self.session.get(SubscriptionPlan, plan_id)
        if not plan:
            raise ValueError("Plan not found")
        while True:
            token_str = secrets.token_urlsafe(8)
            existing = await self.session.get(Token, token_str)
            if existing:
                continue
            token = Token(
                token=token_str,
                duration_days=plan.duration_days,
                name=plan.name,
                price=plan.price,
                plan_id=plan.id,
                status="available",
            )
            self.session.add(token)
            await self.session.commit()
            await self.session.refresh(token)
            return token

    async def validate_token(self, token: str) -> Token | None:
        obj = await self.session.get(Token, token)
        if not obj or obj.status != "available":
            return None
        return obj

    async def mark_token_as_used(self, token: str) -> None:
        obj = await self.session.get(Token, token)
        if obj:
            obj.status = "used"
            await self.session.commit()
