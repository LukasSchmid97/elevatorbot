import asyncio

from anyio import create_task_group
from dis_snek.models import (
    InteractionContext,
    OptionTypes,
    SlashCommandChoice,
    slash_command,
    slash_option,
)

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.commandHelpers.subCommandTemplates import day1completions_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.destinyActivities import raid_to_emblem_hash


class DayOneRaid(BaseScale):
    @slash_command(
        **day1completions_sub_command,
        sub_cmd_name="raid",
        sub_cmd_description="Get the users with a Day One raid completion of the specified raid",
    )
    @slash_option(
        name="raid",
        description="The name of the raid",
        required=True,
        opt_type=OptionTypes.STRING,
        choices=[SlashCommandChoice(name=raid, value=raid) for raid in raid_to_emblem_hash],
    )
    async def _day1_raid(self, ctx: InteractionContext, raid: str):
        async def check_member(player: DestinyAccount):
            # check the members separately to make this faster
            if player:
                result = await player.has_collectible(collectible_id=raid_to_emblem_hash[raid])

                if result:
                    raid_completions.append(player.discord_member.mention)

        raid_completions = []
        async with create_task_group() as tg:
            for member in ctx.guild.members:
                tg.start_soon(check_member, DestinyAccount(ctx=ctx, discord_member=member, discord_guild=ctx.guild))

        embed = embed_message(f"{raid} - Day One Completions")

        if not raid_completions:
            embed.description = "Sadly nobody here cleared this raid on Day One :("

        else:
            embed.description = ", ".join(raid_completions)

        if not ctx.responded:
            await ctx.send(embeds=embed)


def setup(client):
    DayOneRaid(client)
