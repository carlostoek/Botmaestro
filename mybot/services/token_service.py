from __future__ import annotations

import secrets
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Token


class TokenService:
    """Generate and validate invitation tokens."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def generate_token(self, duration_days: int, name: str = "", price: int = 0) -> str:
        """Backward compatible helper used to create a simple token."""
        plan = await self.create_plan(duration_days, name or "plan", price)
        return plan.token

    async def create_plan(self, duration_days: int, name: str, price: int) -> Token:
        """Create a new subscription plan and return it."""
        while True:
            token = secrets.token_urlsafe(8)
            existing = await self.session.get(Token, token)
            if existing:
                continue
            plan = Token(
                token=token,
                duration_days=duration_days,
                name=name,
                price=price,
                status="available",
            )
            self.session.add(plan)
            await self.session.commit()
            await self.session.refresh(plan)
            return plan

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
