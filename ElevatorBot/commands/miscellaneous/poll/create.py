from dis_snek.models import InteractionContext, OptionTypes, slash_command, slash_option

from ElevatorBot.backendNetworking.misc.polls import BackendPolls
from ElevatorBot.commandHelpers.subCommandTemplates import poll_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.poll import Poll


class PollCreate(BaseScale):
    @slash_command(
        **poll_sub_command,
        sub_cmd_name="create",
        sub_cmd_description="Create a new poll",
    )
    @slash_option(
        name="name",
        description="The name the poll should have",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    @slash_option(
        name="description",
        description="The description the poll should have",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    async def create(self, ctx: InteractionContext, name: str, description: str):
        # todo allow images here

        poll = Poll(
            backend=BackendPolls(ctx=ctx, discord_member=ctx.author, guild=ctx.guild),
            name=name,
            description=description,
            guild=ctx.guild,
            channel=ctx.channel,
            author=ctx.author,
        )
        await poll.send()


def setup(client):
    PollCreate(client)
