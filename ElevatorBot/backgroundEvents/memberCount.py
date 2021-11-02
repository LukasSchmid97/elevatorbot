from dis_snek.client import Snake

from ElevatorBot.backgroundEvents import BaseEvent
from ElevatorBot.misc.cache import descend_cache
from ElevatorBot.static.descendOnlyIds import descend_guild_id


class MemberCount(BaseEvent):
    """This updates the member count for descend"""

    def __init__(self):
        interval_minutes = 30
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self, client: Snake):
        # get descend
        descend = await client.get_guild(descend_guild_id)

        # get the channel if exists and update that message
        try:
            channel = await descend_cache.get_member_count(descend_guild=descend)
        except LookupError:
            return

        # update the name
        await channel.edit(
            name=f"𝖬𝖾𝗆𝖻𝖾𝗋𝗌｜{descend.member_count}",
            reason="Member Count Update",
        )
