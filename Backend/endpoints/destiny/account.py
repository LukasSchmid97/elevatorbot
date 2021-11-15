from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.destiny.activities import DestinyActivities
from Backend.core.destiny.profile import DestinyProfile
from Backend.crud import discord_users
from Backend.dependencies import get_db_session
from NetworkingSchemas.basic import BoolModel, NameModel, ValueModel
from NetworkingSchemas.destiny.account import (
    BoolModelRecord,
    DestinyCharactersModel,
    DestinyLowMansModel,
    DestinyTimeInputModel,
    DestinyTimeModel,
    DestinyTimesModel,
    DestinyTriumphScoreModel,
    SeasonalChallengesModel,
)

router = APIRouter(
    prefix="/destiny/{guild_id}/{discord_id}/account",
    tags=["destiny", "account"],
)


@router.get("/name", response_model=NameModel)
async def destiny_name(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return the destiny name"""

    user = await discord_users.get_profile_from_discord_id(db, discord_id)
    return NameModel(name=user.bungie_name)


@router.get("/collectible/{collectible_id}", response_model=BoolModel)
async def has_collectible(
    guild_id: int, discord_id: int, collectible_id: int, db: AsyncSession = Depends(get_db_session)
):
    """Return is the collectible is unlocked"""

    user = await discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)
    return BoolModel(bool=await profile.has_collectible(collectible_hash=collectible_id))


@router.get("/triumph/{triumph_id}", response_model=BoolModelRecord)
async def has_triumph(guild_id: int, discord_id: int, triumph_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return is the triumph is unlocked"""

    user = await discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    return await profile.has_triumph(triumph_hash=triumph_id)


@router.get("/metric/{metric_id}", response_model=ValueModel)
async def metric(guild_id: int, discord_id: int, metric_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return the metric value"""

    user = await discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    # get the metric value
    value = await profile.get_metric_value(metric_hash=metric_id)

    return ValueModel(value=value)


@router.get("/solos", response_model=DestinyLowMansModel)
async def destiny_solos(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return the destiny solos"""

    user = await discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)
    activities = DestinyActivities(db=db, user=user)

    # get the solo data
    return await activities.get_solos()


@router.get("/characters", response_model=DestinyCharactersModel)
async def characters(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return the characters with info on them"""

    user = await discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    # get the characters
    return await profile.get_character_info()


@router.get("/stat/{stat_category}/{stat_name}", response_model=ValueModel)
async def stat(
    guild_id: int, discord_id: int, stat_category: str, stat_name: str, db: AsyncSession = Depends(get_db_session)
):
    """Return the stat value"""

    user = await discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    # get the stat value
    value = await profile.get_stat_value(stat_name=stat_name, stat_category=stat_category)

    return ValueModel(value=value)


@router.get("/stat/{stat_category}/{stat_name}/character/{character_id}", response_model=ValueModel)
async def stat_characters(
    guild_id: int,
    discord_id: int,
    character_id: int,
    stat_category: str,
    stat_name: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Return the stat value by character_id"""

    user = await discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    # get the stat value
    value = await profile.get_stat_value(stat_name=stat_name, stat_category=stat_category, character_id=character_id)

    return ValueModel(value=value)


@router.get("/time", response_model=dict[int | list[int], DestinyTimesModel])
async def time(
    guild_id: int, discord_id: int, time_input: DestinyTimeInputModel, db: AsyncSession = Depends(get_db_session)
):
    """
    Return the time played for the specified modes / activities

    Returns either the mode: int as a key, or the activity_ids: list[int], if they are specified
    """

    user = await discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    entries = []
    if not time_input.activity_ids:
        # loop through the modes
        for mode in time_input.modes:
            entries.append(
                DestinyTimeModel(
                    mode=mode,
                    time_played=await profile.get_time_played(
                        start_time=time_input.start_time,
                        end_time=time_input.end_time,
                        mode=mode,
                        character_class=time_input.character_class,
                    ),
                )
            )

    else:
        # check the total then the activities
        entries.append(
            DestinyTimeModel(
                mode=0,
                time_played=await profile.get_time_played(
                    start_time=time_input.start_time,
                    end_time=time_input.end_time,
                    mode=0,
                    character_class=time_input.character_class,
                ),
            )
        )
        entries.append(
            DestinyTimeModel(
                activity_ids=time_input.activity_ids,
                time_played=await profile.get_time_played(
                    start_time=time_input.start_time,
                    end_time=time_input.end_time,
                    activity_ids=time_input.activity_ids,
                    character_class=time_input.character_class,
                ),
            )
        )

    return DestinyTimesModel(entries=entries)


@router.get("/seasonal_challenges", response_model=SeasonalChallengesModel)
async def seasonal_challenges(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return the seasonal challenges completion ratio"""

    user = await discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    return await profile.get_seasonal_challenges()


@router.get("/triumphs", response_model=DestinyTriumphScoreModel)
async def triumph_score(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return the user's triumph scores"""

    user = await discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    return await profile.get_triumph_score()


@router.get("/artifact", response_model=ValueModel)
async def artifact_level(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return the user's artifact power bonus"""

    user = await discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    return await profile.get_artifact_level()


@router.get("/season_pass", response_model=ValueModel)
async def season_pass_level(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return the user's season pass level"""

    user = await discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    return await profile.get_season_pass_level()


@router.get("/consumable/{consumable_id}", response_model=ValueModel)
async def get_consumable_amount(
    guild_id: int, discord_id: int, consumable_id: int, db: AsyncSession = Depends(get_db_session)
):
    """Gets the amount of the given consumable that the player has"""

    user = await discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    return ValueModel(value=await profile.get_consumable_amount(consumable_id=consumable_id))


@router.get("/max_power", response_model=ValueModel)
async def get_max_power(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Gets the current max power of the player"""

    user = await discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    return ValueModel(value=await profile.get_max_power())
