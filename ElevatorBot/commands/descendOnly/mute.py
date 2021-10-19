import asyncio

from dis_snek.models import InteractionContext
from dis_snek.models import Member
from dis_snek.models import OptionTypes
from dis_snek.models import slash_command
from dis_snek.models import slash_option

from ElevatorBot.commandHelpers.optionTemplates import admin_group
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.discordShortcutFunctions import assign_roles_to_member
from ElevatorBot.misc.discordShortcutFunctions import remove_roles_from_member
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.descendOnlyIds import descend_muted_role_id


class Mute(BaseScale):

    # todo perm
    @slash_command(name="mute", description="Mutes the specified user for specified amount of time", **admin_group)
    @default_user_option(description="Which user to mute", required=True)
    @slash_option(
        name="hours", description="How many hours to mute the user for", required=True, opt_type=OptionTypes.INTEGER
    )
    async def _mute(self, ctx: InteractionContext, user: Member, hours: int):

        await assign_roles_to_member(user, descend_muted_role_id, reason=f"/mute by {ctx.author}")

        status = await ctx.send(
            embeds=embed_message(
                "Success",
                f"Muted {user.mention} for {hours} hours\nI will edit this message once the time is over",
            )
        )

        await asyncio.sleep(hours * 60 * 60)
        await remove_roles_from_member(user, descend_muted_role_id, reason=f"/mute by {ctx.author}")

        await status.edit(embeds=embed_message("Success", f"{user.mention} is no longer muted"))


def setup(client):
    Mute(client)
