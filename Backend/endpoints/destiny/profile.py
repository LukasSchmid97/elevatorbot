from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.dependencies import get_db_session
from Backend import crud
from Backend.schemas.destinyProfile import DestinyProfileModel


router = APIRouter(
    prefix="/profile",
    tags=["destiny", "profile"],
)


@router.get("/discord/{discord_id}", response_model=DestinyProfileModel)
async def discord_get(discord_id: int, db: AsyncSession = Depends(get_db_session)):
    """ Return a users profile """

    profile = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    return DestinyProfileModel.from_orm(profile)


@router.get("/destiny/{destiny_id}", response_model=DestinyProfileModel)
async def discord_get(destiny_id: int, db: AsyncSession = Depends(get_db_session)):
    """ Return a users profile """

    profile = await crud.discord_users.get_profile_from_destiny_id(db, destiny_id)
    return DestinyProfileModel.from_orm(profile)
