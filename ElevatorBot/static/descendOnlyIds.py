from dis_snek import Guild, GuildText
from dis_snek.client.errors import Forbidden

from ElevatorBot.discordEvents.base import ElevatorSnake
from Shared.functions.readSettingsFile import get_setting


class __DescendChannels:
    guild: Guild | int | None = get_setting("DESCEND_GUILD_ID")

    admin_channel: GuildText | int | None = get_setting("DESCEND_CHANNEL_ADMIN_ID")
    bot_dev_channel: GuildText | int | None = get_setting("DESCEND_CHANNEL_BOT_DEV_ID")
    registration_channel: GuildText | int | None = get_setting("DESCEND_CHANNEL_REGISTRATION_ID")
    community_roles_channel: GuildText | int | None = get_setting("DESCEND_CHANNEL_COMMUNITY_ROLES_ID")
    join_log_channel: GuildText | int | None = get_setting("DESCEND_CHANNEL_JOIN_LOG_ID")

    async def init_channels(self, client: ElevatorSnake):
        """Runs on startup to get the channels we use"""
        try:
            self.guild = await client.get_guild(self.guild)
        except Forbidden:
            # loop through all class attributes and set them to None
            for attr, value in self.__dict__.items():
                setattr(self, attr, None)
            return False

        # loop through all class attributes and fill out the channel objs
        for attr, value in self.__dict__.items():
            if attr != "guild":
                # get the channel
                channel = await client.get_channel(value)
                setattr(self, attr, channel)
        return True


descend_channels: __DescendChannels = __DescendChannels()
