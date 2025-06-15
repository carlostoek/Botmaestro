from dataclasses import dataclass, field
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.BOT_TOKEN:
            raise RuntimeError(
                "BOT_TOKEN environment variable is not set. "
                "Create a .env file based on .env.example or set the variable "
                "before running the bot."
            )

        admin_ids = os.getenv("ADMIN_IDS", "")
        if admin_ids:
            try:
                self.ADMIN_IDS = [int(x.strip()) for x in admin_ids.split(",") if x.strip()]
            except ValueError:
                raise RuntimeError("ADMIN_IDS must be a comma-separated list of integers")
        if not self.ADMIN_IDS:
            raise RuntimeError(
                "ADMIN_IDS environment variable is not set. "
                "Specify at least one admin Telegram ID before running the bot."
            )

settings = Settings()
