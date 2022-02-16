from anyio import create_task_group

from ElevatorBot.backgroundEvents.base import BaseEvent
from ElevatorBot.core.destiny.roles import Roles
from ElevatorBot.discordEvents.base import ElevatorSnake
from ElevatorBot.misc.cache import registered_role_cache


class AutomaticRoleAssignment(BaseEvent):
    """Every day, this updates all registered users roles"""

    def __init__(self):
        dow_day_of_week = "*"
        dow_hour = 1
        dow_minute = 0
        super().__init__(
            scheduler_type="cron",
            dow_day_of_week=dow_day_of_week,
            dow_hour=dow_hour,
            dow_minute=dow_minute,
        )

    async def run(self, client: ElevatorSnake):
        # update them in anyio tasks
        async with create_task_group() as tg:
            # loop through all guilds members
            for guild in client.guilds:
                for member in guild.members:
                    # ignore know unregistered people
                    if not registered_role_cache.is_not_registered(member.id):
                        tg.start_soon(Roles(guild=guild, member=member, ctx=None).update)
