from dis_snek.models import (
    ActionRow,
    Button,
    ButtonStyles,
    GuildChannel,
    GuildText,
    InteractionContext,
    OptionTypes,
    slash_option,
    sub_command,
)

from ElevatorBot.commandHelpers.responseTemplates import respond_wrong_channel_type
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.persistentMessages import handle_setup_command


class ClanJoin(BaseScale):

    # todo perms
    @sub_command(
        base_name="setup",
        base_description="Use these commands to setup ElevatorBot on this server",
        group_name="clan",
        group_description="Everything concerning the link from this server to your Destiny 2 clan",
        sub_name="join",
        sub_description="Designate a channel where players can join your clan by pressing a button. They will get an invite by the person which used /setup clan link",
    )
    @slash_option(
        name="channel",
        description="The text channel where the message should be displayed",
        required=True,
        opt_type=OptionTypes.CHANNEL,
    )
    @slash_option(
        name="message_id",
        description="You can input a message ID to have me edit that message instead of sending a new one. Message must be from me and in the input channel",
        required=False,
        opt_type=OptionTypes.INTEGER,
    )
    async def _join(self, ctx: InteractionContext, channel: GuildChannel, message_id: int = None):
        # make sure the channel is a text channel
        if not isinstance(channel, GuildText):
            await respond_wrong_channel_type(ctx=ctx)
            return

        message_name = "clan_join_request"
        components = [
            ActionRow(
                Button(
                    # todo callback
                    custom_id=message_name,
                    style=ButtonStyles.GREEN,
                    label="Click to Join the Linked Destiny 2 Clan",
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
            message_id=message_id,
        )


def setup(client):
    ClanJoin(client)
