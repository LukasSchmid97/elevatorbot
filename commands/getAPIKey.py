from discord import channel

from commands.base_command import BaseCommand
from functions.network import getFreshToken


class getapikey(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] If used in a DM, DMs your API key for bungie back"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        if type(message.channel) == channel.DMChannel:
            with message.channel.typing():
                print('getting apikey')
                if message.author.id is not mentioned_user.id:
                    await message.channel.send("Cant get a different users token. please try again")
                    return
                await message.channel.send(await getFreshToken(message.author.id))
        else:
            await message.channel.send("only usable in DMs, due to privacy/security concerns")
