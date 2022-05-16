import asyncio

from naff import Modal, ParagraphText, slash_command

from ElevatorBot.commandHelpers.optionTemplates import lfg_event_id
from ElevatorBot.commandHelpers.responseTemplates import respond_timeout
from ElevatorBot.commandHelpers.subCommandTemplates import lfg_sub_command
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.destiny.lfg.lfgSystem import LfgMessage
from ElevatorBot.discordEvents.base import ElevatorInteractionContext, ElevatorModalContext
from ElevatorBot.misc.formatting import embed_message


class LfgAlert(BaseModule):
    @slash_command(
        **lfg_sub_command,
        sub_cmd_name="alert",
        sub_cmd_description="Message all users in the event",
    )
    @lfg_event_id()
    async def alert(self, ctx: ElevatorInteractionContext, lfg_id: int):
        # get the message obj
        lfg_message = await LfgMessage.from_lfg_id(ctx=ctx, lfg_id=lfg_id, client=ctx.bot, guild=ctx.guild)

        # error if that is not an lfg message
        if not lfg_message:
            return

        # test if the user is a member
        if ctx.author.id not in lfg_message.joined_ids:
            await ctx.send(
                ephemeral=True,
                embeds=embed_message(
                    "Error",
                    "You can only message events in which you are participating",
                ),
            )
            return

        # get the text from a modal
        modal = Modal(
            title="LFG Alert Content",
            components=[
                ParagraphText(
                    label="The message the participants will receive",
                    custom_id="text",
                    min_length=5,
                    max_length=500,
                    required=True,
                ),
            ],
        )
        await ctx.send_modal(modal=modal)

        # wait 5 minutes for them to fill it out
        try:
            # noinspection PyTypeChecker
            modal_ctx: ElevatorModalContext = await ctx.bot.wait_for_modal(modal=modal, timeout=300)
        except asyncio.TimeoutError:
            # give timeout message
            await respond_timeout(ctx=ctx)
            return

        else:
            # sent the message
            await lfg_message.alert_members(text=modal_ctx.responses["text"], from_member=ctx.author)

            await modal_ctx.send(
                ephemeral=True,
                embeds=embed_message(
                    "Success",
                    "I have send your message",
                ),
            )


def setup(client):
    LfgAlert(client)
