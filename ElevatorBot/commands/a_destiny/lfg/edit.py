from dis_snek import InteractionContext, slash_command

from ElevatorBot.commandHelpers.autocomplete import activities, autocomplete_send_activity_name
from ElevatorBot.commandHelpers.optionTemplates import autocomplete_activity_option, lfg_event_id
from ElevatorBot.commandHelpers.subCommandTemplates import lfg_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.lfg.lfgSystem import LfgMessage
from ElevatorBot.misc.discordShortcutFunctions import has_admin_permission
from ElevatorBot.misc.formatting import embed_message


# todo switch start time / timezone / description / max member overwrite to modals (show current max members)
class LfgEdit(BaseScale):
    @slash_command(
        **lfg_sub_command,
        sub_cmd_name="edit",
        sub_cmd_description="When you fucked up and need to edit an event",
    )
    @lfg_event_id()
    @autocomplete_activity_option(description="Use this is you want to edit the name of the activity", required=False)
    async def edit(self, ctx: InteractionContext, lfg_id: int, activity: str):
        await ctx.send(
            "Please delete / re-create the event for now. This requires an unreleased discord feature", ephemeral=True
        )
        return

        # get the message obj
        lfg_message = await LfgMessage.from_lfg_id(ctx=ctx, lfg_id=lfg_id, client=ctx.bot, guild=ctx.guild)

        # error if that is not an lfg message
        if not lfg_message:
            return

        # test if the user is admin or author
        if ctx.author.id != lfg_message.author_id:
            if not await has_admin_permission(ctx=ctx, member=ctx.author):
                return

        # get the actual activity
        activity = activities[activity]

        # todo modal
        ...

        # # resend msg
        # await lfg_message.send()
        # if section == "Start Time":
        #     await lfg_message.alert_start_time_changed(previous_start_time=old_start_time)

        await ctx.send(
            embeds=embed_message(
                "Success", f"I have edited the post, click [here]({lfg_message.message.jump_url}) to view it"
            ),
            components=[],
        )


def setup(client):
    command = LfgEdit(client)

    # register the autocomplete callback
    command.edit.autocomplete("activity")(autocomplete_send_activity_name)
