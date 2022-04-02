import datetime
import logging
import os
import traceback
import zoneinfo
from enum import Enum, EnumMeta
from typing import Generator, Optional

from dateutil.parser import ParserError, parse
from dis_snek import ComponentContext, InteractionContext

from ElevatorBot.commandHelpers.responseTemplates import respond_invalid_time_input, respond_time_input_in_past
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.destiny.account import DestinyAccount
from ElevatorBot.static.emojis import custom_emojis
from Shared.functions.helperFunctions import get_min_with_tz, get_now_with_tz


async def parse_string_datetime(
    ctx: InteractionContext, time: str, timezone: str = "UTC", can_start_in_past: bool = True
) -> Optional[datetime.datetime]:
    """Parse an input time and return it, or None if that fails"""

    # get start time
    try:
        time = parse(time, dayfirst=True)
    except ParserError:
        await respond_invalid_time_input(ctx=ctx)
        return

    if not time.tzinfo:
        # make that timezone aware
        tz = zoneinfo.ZoneInfo(timezone)
        time = time.replace(tzinfo=tz)

    # make sure that is in the future
    if not can_start_in_past:
        if time < get_now_with_tz():
            await respond_time_input_in_past(ctx=ctx)
            return

    return time


async def parse_datetime_options(
    ctx: InteractionContext,
    expansion: Optional[str] = None,
    season: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    can_start_in_past: bool = True,
) -> tuple[Optional[datetime.datetime], Optional[datetime.datetime]]:
    """
    Parse datetime options and return:

    (start_time, end_time)
    or (None, None) - if something went wrong
    """

    # test if the args are wrong
    wrong_args = False
    if expansion:
        if season or start_time or end_time:
            wrong_args = True
    if season:
        if start_time or end_time:
            wrong_args = True

    if wrong_args:
        await ctx.send(
            ephemeral=True,
            embeds=embed_message(
                "Error",
                f"You can only input the following three combinations. Either: \n{custom_emojis.enter} `expansion` \n{custom_emojis.enter} `season` \n{custom_emojis.enter} `start_time` and/or `end_time`",
            ),
        )
        return None, None

    # default values
    formatted_start_time = get_min_with_tz()
    formatted_end_time = get_now_with_tz()

    if expansion:
        parts = expansion.split("|")
        formatted_start_time = datetime.datetime.fromtimestamp(int(parts[1]), tz=datetime.timezone.utc)
        formatted_end_time = datetime.datetime.fromtimestamp(int(parts[2]), tz=datetime.timezone.utc)

    if season:
        parts = season.split("|")
        formatted_start_time = datetime.datetime.fromtimestamp(int(parts[1]), tz=datetime.timezone.utc)
        formatted_end_time = datetime.datetime.fromtimestamp(int(parts[2]), tz=datetime.timezone.utc)

    if start_time:
        formatted_start_time = await parse_string_datetime(
            ctx=ctx, time=start_time, can_start_in_past=can_start_in_past
        )
        if not formatted_start_time:
            return None, None

    if end_time:
        formatted_end_time = await parse_string_datetime(ctx=ctx, time=end_time, can_start_in_past=can_start_in_past)
        if not formatted_end_time:
            return None, None

    return formatted_start_time, formatted_end_time


async def log_error(
    ctx: InteractionContext | ComponentContext | None, error: Exception, logger: logging.Logger
) -> None:
    """Respond to the context and log error"""

    # get the command name or the component name
    if isinstance(ctx, ComponentContext):
        extra = f"CustomID {ctx.custom_id}"
    else:
        extra = f"CommandName '/{ctx.invoked_name}'"

    # log the error
    logger.exception(
        f"InteractionID '{ctx.interaction_id}' - {extra} - Error '{error}' - Traceback: \n{''.join(traceback.format_tb(error.__traceback__))}"
    )

    # do not send some errors to the user
    catch_errors = ["Unknown interaction", "Interaction has already been acknowledged"]

    if not ctx.responded:
        if any(item in catch_errors for item in str(error)):
            # send a generic error message
            # Note: It probably is my fault
            await ctx.send(
                embeds=embed_message(
                    "Error", "I swear its not my fault - discord did an oopsie\nPlease use the command again"
                )
            )
        else:
            await ctx.send(
                embeds=embed_message(
                    "Error",
                    "Sorry, something went wrong\nThe Error has been logged and will be worked on",
                    str(error),
                )
            )

    # raising error again to making deving easier
    raise error


async def get_character_ids_from_class(profile: DestinyAccount, destiny_class: str) -> Optional[list[int]]:
    """Return the users character_ids that fit the given class or None"""

    result = await profile.get_character_info()

    if not result:
        return

    # loop through the characters and return the correct ids
    character_ids = []
    for character in result.characters:
        if character.character_class == destiny_class:
            character_ids.append(character.character_id)

    return character_ids if character_ids else None


def yield_files_in_folder(folder: str, extension: str) -> Generator:
    """Yields all paths of all files with the correct extension in the specified folder"""

    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(f".{extension}") and not file.startswith("__init__") and not file.startswith("base"):
                file = file.removesuffix(f".{extension}")
                path = os.path.join(root, file)
                yield path.replace("/", ".").replace("\\", ".")


def get_enum_by_name(enum_class: EnumMeta, key: str) -> Enum:
    """Gets the name of the enum"""

    return getattr(enum_class, "_".join(key.split(" ")).upper())


def get_emoji_by_name(enum_class: EnumMeta, key: str) -> Enum:
    """Gets the emoji of the enum"""

    enum = get_enum_by_name(enum_class=enum_class, key=key)
    return getattr(custom_emojis, enum.name.lower())
