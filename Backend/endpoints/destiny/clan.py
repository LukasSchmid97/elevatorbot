from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend import crud
from Backend.core.destiny.clan import DestinyClan
from Backend.core.destiny.profile import DestinyProfile
from Backend.core.errors import CustomException
from Backend.crud import destiny_clan_links, discord_users
from Backend.dependencies import get_db_session
from NetworkingSchemas.destiny.clan import (
    DestinyClanLink,
    DestinyClanMembersModel,
    DestinyClanModel,
)
from NetworkingSchemas.destiny.profile import DestinyProfileModel

router = APIRouter(
    prefix="/destiny/clan/{guild_id}",
    tags=["destiny", "clan"],
)


@router.get("/get", response_model=DestinyClanModel)  # has test
async def get_clan(guild_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return the linked destiny clan"""

    clan = DestinyClan(db=db, guild_id=guild_id)

    # get name and id
    return await clan.get_clan()


@router.get("/members", response_model=DestinyClanMembersModel)  # has test
async def get_clan_members(guild_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return the clan members"""

    clan = DestinyClan(db=db, guild_id=guild_id)

    members = await clan.get_clan_members()

    return DestinyClanMembersModel(members=members)


@router.get("/members/no_cache", response_model=DestinyClanMembersModel)  # has test
async def get_clan_members_no_cache(guild_id: int, db: AsyncSession = Depends(get_db_session)):
    """Return the clan members without using any cached bungie data"""

    clan = DestinyClan(db=db, guild_id=guild_id)

    members = await clan.get_clan_members(use_cache=False)

    return DestinyClanMembersModel(members=members)


@router.get("/members/search/{search_phrase}", response_model=DestinyClanMembersModel)  # has test
async def search_clan_members(guild_id: int, search_phrase: str, db: AsyncSession = Depends(get_db_session)):
    """Return the clan members"""

    clan = DestinyClan(db=db, guild_id=guild_id)

    members = await clan.search_clan_for_member(member_name=search_phrase)

    return DestinyClanMembersModel(members=members)


@router.post("/{discord_id}/link/", response_model=DestinyClanLink)  # has test
async def link_clan(
    guild_id: int,
    discord_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Links the discord guild to the destiny clan"""

    user = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    profile = DestinyProfile(db=db, user=user)
    user_clan = await profile.get_clan()

    # check if discord user is admin
    clan = DestinyClan(db=db, user=user, guild_id=guild_id)
    if not await clan.is_clan_admin(clan_id=user_clan.id):
        raise CustomException("ClanNoPermissions")

    await crud.destiny_clan_links.link(
        db=db, discord_id=discord_id, discord_guild_id=guild_id, destiny_clan_id=user_clan.id
    )

    return DestinyClanLink(success=True, clan_name=user_clan.name)


@router.delete("/{discord_id}/unlink/", response_model=DestinyClanLink)  # has test
async def unlink_clan(
    guild_id: int,
    discord_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Unlinks the discord guild from the destiny clan"""

    profile = await crud.discord_users.get_profile_from_discord_id(db, discord_id)
    clan = DestinyClan(db=db, user=profile, guild_id=guild_id)

    linked_clan = await clan.get_clan()

    await crud.destiny_clan_links.unlink(
        db=db,
        discord_guild_id=guild_id,
    )

    return DestinyClanLink(success=True, clan_name=linked_clan.name)


@router.post("/invite/{discord_id}/", response_model=DestinyProfileModel)  # has test
async def invite(
    guild_id: int,
    discord_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Invite discord_id to the clan linked to the guild_id"""

    # get the clan link
    link = await destiny_clan_links.get_link(db=db, discord_guild_id=guild_id)

    # get the data for the users
    clan_admin_user = await discord_users.get_profile_from_discord_id(db=db, discord_id=link.linked_by_discord_id)
    to_invite_user = await discord_users.get_profile_from_discord_id(db=db, discord_id=discord_id)

    # invite to the clan
    clan = DestinyClan(db=db, user=clan_admin_user, guild_id=guild_id)
    await clan.invite_to_clan(to_invite_destiny_id=to_invite_user.destiny_id, to_invite_system=to_invite_user.system)

    return DestinyProfileModel.from_orm(to_invite_user)


@router.post("/kick/{discord_id}/", response_model=DestinyProfileModel)  # has test
async def kick(
    guild_id: int,
    discord_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Kick discord_id from the clan linked to the guild_id"""

    # get the clan link
    link = await destiny_clan_links.get_link(db=db, discord_guild_id=guild_id)

    # get the data for the users
    clan_admin_user = await discord_users.get_profile_from_discord_id(db=db, discord_id=link.linked_by_discord_id)
    to_kick_user = await discord_users.get_profile_from_discord_id(db=db, discord_id=discord_id)

    # kick from clan
    clan = DestinyClan(db=db, guild_id=guild_id, user=clan_admin_user)
    await clan.remove_from_clan(to_remove_destiny_id=to_kick_user.destiny_id, to_remove_system=to_kick_user.system)

    return DestinyProfileModel.from_orm(to_kick_user)
