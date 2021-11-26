import logging
import traceback

from dis_snek import Snake
from dis_snek.models import ComponentContext, InteractionContext

from ElevatorBot.misc.helperFunctions import log_error


class CustomErrorSnake(Snake):
    async def on_error(self, source: str, error: Exception, *args, **kwargs):
        """Gets triggered after an error occurs (not in commands / components)"""

        # log the error
        logger = logging.getLogger("generalExceptions")
        logger.exception(
            f"Source '{source}' - Error '{error}' - Traceback: \n{''.join(traceback.format_tb(error.__traceback__))}"
        )

        # raising error again to making deving easier
        raise error

    async def on_command(self, ctx: InteractionContext):
        """Gets triggered after a slash command is run"""

        # log the command
        logger = logging.getLogger("commands")
        logger.info(
            f"InteractionID '{ctx.interaction_id}' - CommandName '/{ctx.invoked_name}' - Kwargs '{ctx.kwargs}' - DiscordName '{ctx.author.name}' - DiscordID '{ctx.author.id}' - GuildID '{ctx.guild.id}' - ChannelID '{ctx.channel.id}'"
        )

    async def on_command_error(self, ctx: InteractionContext, error: Exception, *args, **kwargs):
        """Gets triggered on slash command errors"""

        await log_error(ctx=ctx, error=error, situation="commandsExceptions")

    async def on_component(self, ctx: InteractionContext):
        """Gets triggered after a component callback is run"""

        # log the command
        logger = logging.getLogger("components")
        logger.info(
            f"InteractionID '{ctx.interaction_id}' - Component '{ctx.invoked_name}' - Target '{ctx.target_id}' - DiscordName '{ctx.author.name}' - DiscordID '{ctx.author.id}' - GuildID '{ctx.guild.id}' - ChannelID '{ctx.channel.id}'"
        )

    async def on_component_error(self, ctx: ComponentContext, error: Exception, *args, **kwargs):
        """Gets triggered on component callback errors"""

        await log_error(ctx=ctx, error=error, situation="componentsExceptions")
