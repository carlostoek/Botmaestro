from __future__ import annotations

import secrets
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Token


class TokenService:
    """Generate and validate invitation tokens."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def generate_token(self, duration_days: int) -> str:
        while True:
            token = secrets.token_urlsafe(8)
            existing = await self.session.get(Token, token)
            if existing:
                continue
            self.session.add(Token(token=token, duration_days=duration_days))
            await self.session.commit()
            return token

    async def validate_token(self, token: str) -> int | None:
        obj = await self.session.get(Token, token)
        if not obj or obj.used:
            return None
        return obj.duration_days

    async def mark_token_as_used(self, token: str) -> None:
        obj = await self.session.get(Token, token)
        if obj:
            obj.used = True
            await self.session.commit()
