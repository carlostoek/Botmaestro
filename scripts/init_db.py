import asyncio

from mybot.database.setup import init_db, get_session
from mybot.services.achievement_service import AchievementService
from mybot.services.level_service import LevelService
from mybot.services.mission_service import MissionService

DEFAULT_MISSIONS = [
    {
        "name": "Daily Check-in",
        "description": "Registra tu actividad diaria con /checkin",
        "points_reward": 10,
        "mission_type": "daily",
        "requires_action": False,
        "action_data": None,
    },
    {
        "name": "Primer Mensaje",
        "description": "Envía tu primer mensaje en el chat",
        "points_reward": 5,
        "mission_type": "one_time",
        "requires_action": False,
        "action_data": None,
    },
]

async def main() -> None:
    await init_db()
    Session = await get_session()
    async with Session() as session:
        await AchievementService(session).ensure_achievements_exist()
        level_service = LevelService(session)
        await level_service._init_levels()

        mission_service = MissionService(session)
        existing = await mission_service.get_active_missions()
        if not existing:
            for m in DEFAULT_MISSIONS:
                await mission_service.create_mission(
                    m["name"],
                    m["description"],
                    m["points_reward"],
                    m["mission_type"],
                    m["requires_action"],
                    m["action_data"],
                )
    print("Database initialised")

if __name__ == "__main__":
    asyncio.run(main())
