from naff import slash_command

from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.destiny.dayOneRace import DayOneRace
from ElevatorBot.discordEvents.base import ElevatorInteractionContext
from Shared.functions.readSettingsFile import get_setting

# =============
# Descend Only!
# =============


class DayOneRaceCommand(BaseModule):

    # todo perms
    @slash_command(
        name="day_one_raid_race",
        description="Starts the Day One raid completion announcer",
        scopes=get_setting("COMMAND_GUILD_SCOPE"),
    )
    async def day_one_raid_race(self, ctx: ElevatorInteractionContext):
        if ctx.author.id != 238388130581839872:
            await ctx.send(
                "This is blocked for now, since it it waiting for a vital unreleased discord feature", ephemeral=True
            )
            return

        racer = DayOneRace(ctx=ctx)
        await racer.start()


def setup(client):
    DayOneRaceCommand(client)
