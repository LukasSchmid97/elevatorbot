import logging

from dis_snek import Snake
from dis_snek.models import ComponentContext, InteractionContext

from ElevatorBot.misc.helperFunctions import log_error


class CustomErrorSnake(Snake):
    async def on_command(self, ctx: InteractionContext):
        """Gets triggered after a slash command is run"""

        # print the command
        print (f"{ctx.author.display_name} used '/{ctx.name}' with kwargs '{ctx.kwargs}'")

        # log the command
        logger = logging.getLogger("commands")
        logger.info(
            f"InteractionID '{ctx.interaction_id}' - User '{ctx.author.name}' with discordID '{ctx.author.id}' executed '/{ctx.name}' with kwargs '"
            f"{ctx.kwargs}' in guildID '{ctx.guild.id}', channelID '{ctx.channel.id}'"
        )

    async def on_command_error(self, ctx: InteractionContext, error: Exception):
        """Gets triggered on slash command errors"""

        await log_error(ctx=ctx, error=error, situation="commands")

    async def on_component(self, ctx: InteractionContext):
        """Gets triggered after a component callback is run"""

        # log the command
        logger = logging.getLogger("interactions")
        logger.info(
            f"InteractionID '{ctx.interaction_id}' - User '{ctx.author.name}' with discordID '{ctx.author.id}' clicked on componentType '{ctx.component_type}', componentID '{ctx.component_id}' in guildID '{ctx.origin_message.guild.id}', channelID '{ctx.origin_message.channel.id}', messageID '{ctx.origin_message.id}'"
        )

    async def on_component_error(self, ctx: ComponentContext, error: Exception):
        """Gets triggered on component callback errors"""

        await log_error(ctx=ctx, error=error, situation="components")
