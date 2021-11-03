from dis_snek.models import (
    InteractionContext,
    OptionTypes,
    Role,
    slash_command,
    slash_option,
)

from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile
from ElevatorBot.commandHelpers.subCommandTemplates import setup_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.persistentMessages import (
    PersistentMessages,
    handle_setup_command,
)
from ElevatorBot.misc.cache import registered_role_cache
from ElevatorBot.misc.formating import embed_message


class RegisteredRole(BaseScale):

    # todo perms
    @slash_command(
        **setup_sub_command,
        sub_cmd_name="registered_role",
        sub_cmd_description="Assign the role that is given to people that /register",
    )
    @slash_option(
        name="role",
        description="The role to link",
        required=True,
        opt_type=OptionTypes.ROLE,
    )
    async def _registered_role(self, ctx: InteractionContext, role: Role):
        # cheat a bit and register the role as a persistent message
        persistent_messages = PersistentMessages(ctx=ctx, guild=ctx.guild, message_name="registered_role")
        persistent_messages.hidden = True

        result = await persistent_messages.upsert(channel_id=role.id)
        if not result:
            return

        # save in cache
        registered_role_cache.guild_to_role.update({ctx.guild.id: role})

        await ctx.send(
            embeds=embed_message("Success", f"{role.mention} is now assigned to everyone that is registered")
        )

        # check all members
        for member in ctx.guild.members:
            # check if member is not pending
            if not member.pending:
                destiny_profile = DestinyProfile(
                    ctx=ctx, client=ctx.bot, discord_member=member, discord_guild=ctx.guild
                )
                await destiny_profile.assign_registration_role()


def setup(client):
    RegisteredRole(client)
