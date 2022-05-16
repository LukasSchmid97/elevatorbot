from naff import slash_command

from ElevatorBot.commands.base import BaseModule
from ElevatorBot.discordEvents.base import ElevatorInteractionContext
from Shared.functions.readSettingsFile import get_setting

# =============
# Descend Only!
# =============


class Socialist(BaseModule):

    # todo perms
    @slash_command(name="socialist", description="Spams `#socialist` 🙃", scopes=get_setting("COMMAND_GUILD_SCOPE"))
    async def socialist(self, ctx: ElevatorInteractionContext):
        """Spams #socialist"""

        await ctx.send("No 🙃")


def setup(client):
    Socialist(client)
