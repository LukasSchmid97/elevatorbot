from dis_snek.client import Snake
from dis_snek.models import ActionRow
from dis_snek.models import Button
from dis_snek.models import ButtonStyles
from dis_snek.models import InteractionContext
from dis_snek.models import Scale
from dis_snek.models import slash_command

from ElevatorBot.misc.formating import embed_message
from settings import BUNGIE_OAUTH


class Register(Scale):
    def __init__(self, client):
        self.client: Snake = client

    @slash_command(name="register", description="Link your Destiny 2 account with ElevatorBot")
    async def _register(self, ctx: InteractionContext):

        # not in dms
        if not ctx.guild:
            await ctx.send("Error" "Please use this command in your clans bot-channel")
            return

        # send the link to click on in a hidden embed
        components = [
            ActionRow(
                Button(
                    style=ButtonStyles.URL,
                    label=f"Registration Link",
                    url=f"""https://www.bungie.net/en/oauth/authorize?client_id={BUNGIE_OAUTH}&response_type=code&state={f"{ctx.author.id}:{ctx.guild.id}:{ctx.channel.id}"}""",
                ),
            ),
        ]

        await ctx.send(
            ephemeral=True,
            components=components,
            embeds=embed_message(
                f"Registration",
                f"Use the button below to registration with me",
                "Please be aware that I will need a while to process your data after you registration for the first time, so I might react very slowly to your first commands.",
            ),
        )


def setup(client):
    Register(client)
