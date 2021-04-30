from events.base_event import BaseEvent
from functions.database import getPersistentMessage


class GetMemberCount(BaseEvent):
    """ Updates the member count channel to show how many members are currently in it """
    def __init__(self):
        interval_minutes = 30  # Set the interval for this event
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    # Override the run() method
    # It will be called once every {interval_minutes} minutes
    async def run(self, client):
        # loop through all guilds, get the channel id if exists and update that
        for guild in client.guilds:
            result = await getPersistentMessage("memberCount", guild.id)
            if not result:
                continue
            channel = guild.get_channel(result[0])
            if not channel:
                continue

            # update the name - font is "math sans" from "https://qaz.wtf/u/convert.cgi"
            await channel.edit(name=f"Members｜{guild.member_count}", reason="Member Count Update")


class GetBoosterCount(BaseEvent):
    """ Updates the booster count channel to show how many members are currently in it """
    def __init__(self):
        interval_minutes = 30  # Set the interval for this event
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    # Override the run() method
    # It will be called once every {interval_minutes} minutes
    async def run(self, client):
        # loop through all guilds, get the channel id if exists and update that
        for guild in client.guilds:
            result = await getPersistentMessage("boosterCount", guild.id)
            if not result:
                continue
            channel = guild.get_channel(result[0])
            if not channel:
                continue

            # update the name
            await channel.edit(name=f"Boosters｜{guild.premium_subscription_count}", reason="Booster Count Update")
