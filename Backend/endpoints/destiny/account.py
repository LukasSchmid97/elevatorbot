from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend import crud
from Backend.core.destiny.profile import DestinyProfile
from Backend.dependencies import get_db_session
from Backend.schemas.destiny.account import (
    DestinyCharactersModel,
    DestinyLastInputModel,
    DestinyNameModel,
    DestinyStatModel,
    DestinyTimeInputModel,
    DestinyTimeModel,
)
from Backend.schemas.destiny.profile import DestinyLowMansModel

router = APIRouter(
    prefix="/destiny/{guild_id}/{discord_id}/account",
    tags=["destiny", "account"],
)


@router.get("/name", response_model=DestinyNameModel)
async def destiny_name(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return the destiny name"""

    user = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    return DestinyNameModel(name=user.bungie_name)


@router.get("/solos", response_model=DestinyLowMansModel)
async def destiny_solos(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return the destiny solos"""

    user = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    # get the solo data
    return await profile.get_solos()


@router.get("/characters", response_model=DestinyCharactersModel)
async def characters(guild_id: int, discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return the characters with info on them"""

    user = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    # get the characters
    return await profile.get_character_info()


@router.get("/stat/{stat_category}/{stat_name}", response_model=DestinyStatModel)
async def stat(
    guild_id: int, discord_id: int, stat_category: str, stat_name: str, db: AsyncSession = Depends(get_db_session)
):
    """Return the stat value"""

    user = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    # get the stat value
    value = await profile.get_stat_value(stat_name=stat_name, stat_category=stat_category)

    return DestinyStatModel(value=value)


@router.get("/stat/{stat_category}/{stat_name}/character/{character_id}", response_model=DestinyStatModel)
async def stat_characters(
    guild_id: int,
    discord_id: int,
    character_id: int,
    stat_category: str,
    stat_name: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Return the stat value by character_id"""

    user = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    # get the stat value
    value = await profile.get_stat_value(stat_name=stat_name, stat_category=stat_category, character_id=character_id)

    return DestinyStatModel(value=value)


@router.get("/time", response_model=dict[int | list[int], DestinyTimeModel])
async def time(
    guild_id: int, discord_id: int, time_input: DestinyTimeInputModel, db: AsyncSession = Depends(get_db_session)
):
    """
    Return the time played for the specified modes / activities

    Returns either the mode: int as a key, or the activity_ids: list[int], if they are specified
    """

    user = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    result = {}
    if not time_input.activity_ids:
        # loop through the modes
        for mode in time_input.modes:
            result.update(
                {
                    mode: await profile.get_time_played(
                        start_time=time_input.start_time,
                        end_time=time_input.end_time,
                        mode=mode,
                        character_class=time_input.character_class,
                    )
                }
            )
    else:
        # check the total then the activities
        result.update(
            {
                0: await profile.get_time_played(
                    start_time=time_input.start_time,
                    end_time=time_input.end_time,
                    mode=0,
                    character_class=time_input.character_class,
                ),
                time_input.activity_ids: await profile.get_time_played(
                    start_time=time_input.start_time,
                    end_time=time_input.end_time,
                    activity_ids=time_input.activity_ids,
                    character_class=time_input.character_class,
                ),
            }
        )

    return result


@router.get("/last", response_model=aaaaaaaa)
async def last(
    guild_id: int, discord_id: int, time_input: DestinyLastInputModel, db: AsyncSession = Depends(get_db_session)
):
    """Return information about the last completed activity"""

    user = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)

    return result
