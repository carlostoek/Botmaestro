from __future__ import annotations

from datetime import datetime
from secrets import token_urlsafe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import SubscriptionPlan


class SubscriptionPlanService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_plan(self, created_by: int, name: str, price: int, duration_days: int) -> SubscriptionPlan:
        token = token_urlsafe(8)
        plan = SubscriptionPlan(
            token=token,
            name=name,
            price=price,
            duration_days=duration_days,
            created_by=created_by,
            status="available",
        )
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        return plan

    async def get_plan(self, token: str) -> SubscriptionPlan | None:
        stmt = select(SubscriptionPlan).where(SubscriptionPlan.token == token)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def use_plan(self, token: str, user_id: int) -> SubscriptionPlan | None:
        plan = await self.get_plan(token)
        if not plan or plan.status != "available":
            return None
        plan.status = "used"
        plan.used_by = user_id
        plan.used_at = datetime.utcnow()
        await self.session.commit()
        return plan
