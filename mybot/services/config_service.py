from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import Config


class ConfigService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_config(self, key: str) -> str | None:
        stmt = select(Config).where(Config.key == key)
        result = await self.session.execute(stmt)
        config = result.scalar_one_or_none()
        return config.value if config else None

    async def set_config(self, key: str, value: str) -> None:
        cfg = await self.session.get(Config, key)
        if cfg:
            cfg.value = value
        else:
            cfg = Config(key=key, value=value)
            self.session.add(cfg)
        await self.session.commit()

    async def get_pricing(self) -> tuple[str, str] | None:
        period = await self.get_config("price_period")
        amount = await self.get_config("price_amount")
        if period is None or amount is None:
            return None
        return period, amount

    async def set_pricing(self, period: str, amount: str) -> None:
        await self.set_config("price_period", period)
        await self.set_config("price_amount", amount)

    async def set_price(self, period: str, amount: str) -> None:
        await self.set_config(f"price_{period}", amount)

    async def get_price(self, period: str) -> str | None:
        return await self.get_config(f"price_{period}")
