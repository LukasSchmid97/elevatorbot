from naff import CommandTypes, context_menu

from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.misc.timestamps import get_timestamp_embed
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message


class TimestampsCommands(BaseModule):
    """
    Format all (relative) dates and times in the message
    """

    @context_menu(name="Get Timestamps", context_type=CommandTypes.MESSAGE)
    async def get_timestamp(self, ctx: ElevatorInteractionContext):
        # parse datetimes
        if embed := await get_timestamp_embed(search_string=ctx.target.content.upper()):
            await ctx.send(embeds=embed)

        # no datetimes found
        else:
            embed = embed_message(title="Error", description="No times or dates found in message")
            await ctx.send(embeds=embed)


def setup(client):
    TimestampsCommands(client)
