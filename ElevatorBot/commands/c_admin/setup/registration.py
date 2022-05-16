from typing import Optional

from naff import ActionRow, Button, ButtonStyles, ChannelTypes, GuildChannel, OptionTypes, slash_command, slash_option

from ElevatorBot.commandHelpers.subCommandTemplates import setup_sub_command
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.misc.persistentMessages import handle_setup_command
from ElevatorBot.discordEvents.base import ElevatorInteractionContext


class Registration(BaseModule):

    # todo perms
    @slash_command(
        **setup_sub_command,
        sub_cmd_name="registration",
        sub_cmd_description="Designate a channel in which user can register with me by pressing a button",
    )
    @slash_option(
        name="channel",
        description="The text channel where the message should be displayed",
        required=True,
        opt_type=OptionTypes.CHANNEL,
        channel_types=[ChannelTypes.GUILD_TEXT],
    )
    @slash_option(
        name="message_id",
        description="You can input a message ID (needs to be from me and selected channel) to have me edit that message",
        required=False,
        opt_type=OptionTypes.STRING,
    )
    async def registration(
        self, ctx: ElevatorInteractionContext, channel: GuildChannel, message_id: Optional[str] = None
    ):
        if ctx.author.id != 238388130581839872:
            await ctx.send(
                "This is blocked for now, since it it waiting for a vital unreleased discord feature", ephemeral=True
            )
            return

        message_name = "registration"
        components = [
            ActionRow(
                Button(
                    custom_id=message_name,
                    style=ButtonStyles.GREEN,
                    label="Click to Connect your Destiny 2 Account",
                ),
            ),
        ]
        await handle_setup_command(
            ctx=ctx,
            message_name=message_name,
            channel=channel,
            send_message=True,
            send_components=components,
            send_message_content="⁣",
            message_id=int(message_id) if message_id else None,
        )


def setup(client):
    Registration(client)
