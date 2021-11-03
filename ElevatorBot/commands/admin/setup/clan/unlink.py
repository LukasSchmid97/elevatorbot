from dis_snek.models import InteractionContext, slash_command

from ElevatorBot.backendNetworking.destiny.clan import DestinyClan
from ElevatorBot.commandHelpers.subCommandTemplates import (
    setup_sub_command,
    setup_sub_command_clan_group,
)
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message


class ClanUnlink(BaseScale):
    """Unlink the current Destiny 2 clan the discord server this was executed in"""

    # todo perms
    @slash_command(
        **setup_sub_command,
        **setup_sub_command_clan_group,
        sub_cmd_name="unlink",
        sub_cmd_description="Unlink the current Destiny 2 clan with this server",
    )
    async def _unlink(
        self,
        ctx: InteractionContext,
    ):

        clan = DestinyClan(ctx=ctx, client=ctx.bot, discord_member=ctx.author, discord_guild=ctx.guild)
        result = await clan.unlink()

        if not result:
            return

        await ctx.send(
            embeds=embed_message(
                "Success",
                f"This discord server has been successfully unlinked from the clan `{result.clan_name}`",
            )
        )


def setup(client):
    ClanUnlink(client)
