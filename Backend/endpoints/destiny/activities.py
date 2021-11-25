from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend import crud
from Backend.core.destiny.activities import DestinyActivities
from Backend.crud import destiny_manifest
from Backend.dependencies import get_db_session
from NetworkingSchemas.destiny.activities import (
    DestinyActivitiesModel,
    DestinyActivityDetailsModel,
    DestinyActivityInputModel,
    DestinyActivityOutputModel,
    DestinyLastInputModel,
)

router = APIRouter(
    prefix="/activities",
    tags=["destiny", "activities"],
)


@router.get("/get/all", response_model=DestinyActivitiesModel)
async def get_all(db: AsyncSession = Depends(get_db_session)):
    """Return all activities and their hashes"""

    return DestinyActivitiesModel(activities=await destiny_manifest.get_all_activities(db=db))


@router.get("/{guild_id}/{discord_id}/last", response_model=DestinyActivityDetailsModel)
async def last(
    guild_id: int, discord_id: int, last_input: DestinyLastInputModel, db: AsyncSession = Depends(get_db_session)
):
    """Return information about the last completed activity"""

    user = await crud.discord_users.get_profile_from_discord_id(db, discord_id)

    # update the users db entries
    activities = DestinyActivities(db=db, user=user)
    await activities.update_activity_db()

    return await activities.get_last_played(
        mode=last_input.mode if last_input.mode else 0,
        activity_ids=last_input.activity_ids,
        character_class=last_input.character_class,
        completed=last_input.completed,
    )


@router.get("/{guild_id}/{discord_id}/activity", response_model=DestinyActivityOutputModel)
async def activity(
    guild_id: int,
    discord_id: int,
    activity_input: DestinyActivityInputModel,
    db: AsyncSession = Depends(get_db_session),
):
    """Return information about the user their stats in the supplied activity ids"""

    user = await crud.discord_users.get_profile_from_discord_id(db, discord_id)

    # update the users db entries
    activities = DestinyActivities(db=db, user=user)
    await activities.update_activity_db()

    return await activities.get_activity_stats(
        activity_ids=activity_input.activity_ids,
        mode=activity_input.mode,
        character_class=activity_input.character_class,
        character_ids=activity_input.character_ids,
        start_time=activity_input.start_time,
        end_time=activity_input.end_time,
    )


@router.get("/get/grandmaster", response_model=DestinyActivitiesModel)
async def activity(db: AsyncSession = Depends(get_db_session)):
    """Return information about all grandmaster nfs from the DB"""

    return DestinyActivitiesModel(activities=await destiny_manifest.get_grandmaster_nfs(db=db))
