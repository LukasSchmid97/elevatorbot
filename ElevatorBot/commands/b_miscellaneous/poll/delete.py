from dis_snek import InteractionContext, OptionTypes, slash_command, slash_option

from ElevatorBot.commandHelpers.subCommandTemplates import poll_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.poll import Poll


class PollDelete(BaseScale):
    @slash_command(
        **poll_sub_command,
        sub_cmd_name="delete",
        sub_cmd_description="Delete an existing poll",
    )
    @slash_option(
        name="poll_id", description="The ID of the poll", opt_type=OptionTypes.INTEGER, required=True, min_value=0
    )
    async def delete(self, ctx: InteractionContext, poll_id: int):
        poll = await Poll.from_poll_id(poll_id=poll_id, ctx=ctx)

        if poll:
            await poll.delete(ctx=ctx)


def setup(client):
    PollDelete(client)