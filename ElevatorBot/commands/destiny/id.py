from dis_snek.models import InteractionContext
from dis_snek.models import Member
from dis_snek.models import slash_command

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commandHelpers.optionTemplates import destiny_group
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message


class IdGet(BaseScale):
    @slash_command(
        name="id",
        description="Get the users Bungie Name, which can be used to join people in Destiny 2 without adding them as a friend",
        **destiny_group,
    )
    @default_user_option()
    async def _id(self, ctx: InteractionContext, user: Member = None):

        # assign user to be the mentioned user if applicable
        user = user if user else ctx.author

        destiny_profile = DestinyAccount(client=ctx.bot, discord_member=user, discord_guild=ctx.guild)
        result = await destiny_profile.get_destiny_name()

        if not result:
            await result.send_error_message(ctx, hidden=True)
        else:
            await ctx.send(
                embeds=embed_message(
                    f"{user.display_name}'s Join Code",
                    f"`/join {result.result['name']}`",
                ),
            )


def setup(client):
    IdGet(client)
