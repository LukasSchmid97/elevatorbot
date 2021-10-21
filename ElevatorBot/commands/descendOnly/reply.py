# from discord.ext.commands import Cog
# from discord_slash import cog_ext
# from discord_slash import SlashContext
# from discord_slash.utils.manage_commands import create_option
#
# from ElevatorBot.commandHelpers.optionTemplates import default_user_option
# from ElevatorBot.commandHelpers.permissionTemplates import permissions_admin
#
#
# class Reply(Cog):
#     def __init__(self, client):
#         self.client = client
#
#     @cog_ext.cog_slash(
#         name="reply",
#         description="Send a message to whoever got tagged above",
#         options=[
#             create_option(
#                 name="message",
#                 description="What message to reply with",
#                 option_type=3,
#                 required=True,
#             ),
#             default_user_option("Which user to reply to"),
#         ],
#         default_permission=False,
#         permissions=permissions_admin, scope=COMMAND_GUILD_SCOPE
#     )
#     async def _reply(self, ctx: SlashContext, message: str, user=None):
#         pass
#
#
# def setup(client):
#     Reply(client)
