import asyncio
import datetime
from typing import Optional

from sqlalchemy import distinct, func, not_, select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud.base import CRUDBase
from Backend.database.models import (
    Activities,
    ActivitiesFailToGet,
    ActivitiesUsers,
    ActivitiesUsersWeapons,
    DestinyActivityDefinition,
)
from NetworkingSchemas.destiny.roles import TimePeriodModel


class CRUDActivitiesFailToGet(CRUDBase):
    async def get_all(self, db: AsyncSession) -> list[ActivitiesFailToGet]:
        """Get all missing pgcr ids"""

        return await self._get_all(db=db)

    async def insert(self, db: AsyncSession, instance_id: int, period: datetime.datetime):
        """Insert missing pgcr"""

        if await self._get_with_key(db=db, primary_key=instance_id) is None:
            await self._insert(db=db, to_create=ActivitiesFailToGet(instance_id=instance_id, period=period))

    async def delete(self, db: AsyncSession, obj: ActivitiesFailToGet):
        """Insert missing pgcr"""

        await self._delete(db=db, obj=obj)


class CRUDActivities(CRUDBase):
    async def get(self, db: AsyncSession, instance_id: int) -> Optional[Activities]:
        """Get the activity with the instance_id"""

        return await self._get_with_key(db=db, primary_key=instance_id)

    async def get_user_stats(self, db: AsyncSession, destiny_id: int, instance_id: int) -> list[ActivitiesUsers]:
        """Get the activity with the instance_id"""

        return await self._get_multi(db=db, instance_id=instance_id, destiny_id=destiny_id)

    async def get_activity_name(self, db: AsyncSession, activity_id: int) -> str:
        """Get the activity name"""

        query = select(DestinyActivityDefinition.name).filter(DestinyActivityDefinition.reference_id == activity_id)

        result = await self._execute_query(db=db, query=query)
        result = result.scalar()
        if not result:
            raise CustomException("UnknownError")

        return result

    async def insert(self, db: AsyncSession, instance_id: int, activity_time: datetime, pgcr: dict):
        """Get the activity with the instance_id"""

        # get this to not accidentally insert the same thing twice
        async with asyncio.Lock():
            return await self.__locked_insert(db=db, instance_id=instance_id, activity_time=activity_time, pgcr=pgcr)

    async def __locked_insert(self, db: AsyncSession, instance_id: int, activity_time: datetime, pgcr: dict):
        """Actually do the insert"""

        # does the activity exist?
        if self.get(db=db, instance_id=instance_id):
            return

        to_create = []

        # build the activity
        activity = Activities(
            instance_id=instance_id,
            period=activity_time,
            reference_id=pgcr["activityDetails"]["referenceId"],
            director_activity_hash=pgcr["activityDetails"]["directorActivityHash"],
            starting_phase_index=pgcr["startingPhaseIndex"],
            mode=pgcr["activityDetails"]["mode"],
            modes=pgcr["activityDetails"]["modes"],
            is_private=pgcr["activityDetails"]["isPrivate"],
            system=pgcr["activityDetails"]["membershipType"],
        )

        # loop through the members of the activity and append that data
        for player_pgcr in pgcr["entries"]:
            player = ActivitiesUsers(
                destiny_id=player_pgcr["player"]["destinyUserInfo"]["membershipId"],
                bungie_name=f"""{player_pgcr["player"]["destinyUserInfo"]["bungieGlobalDisplayName"]}#{player_pgcr["player"]["destinyUserInfo"]["bungieGlobalDisplayNameCode"]}""",
                character_id=player_pgcr["characterId"],
                character_class=player_pgcr["player"]["characterClass"]
                if "characterClass" in player_pgcr["player"]
                else None,
                character_level=player_pgcr["player"]["characterLevel"],
                system=player_pgcr["player"]["destinyUserInfo"]["membershipType"],
                light_level=player_pgcr["player"]["lightLevel"],
                emblem_hash=player_pgcr["player"]["emblemHash"],
                standing=player_pgcr["standing"],
                assists=int(player_pgcr["values"]["assists"]["basic"]["value"]),
                completed=int(player_pgcr["values"]["completed"]["basic"]["value"]),
                deaths=int(player_pgcr["values"]["deaths"]["basic"]["value"]),
                kills=int(player_pgcr["values"]["kills"]["basic"]["value"]),
                opponents_defeated=int(player_pgcr["values"]["opponentsDefeated"]["basic"]["value"]),
                efficiency=player_pgcr["values"]["efficiency"]["basic"]["value"],
                kills_deaths_ratio=player_pgcr["values"]["killsDeathsRatio"]["basic"]["value"],
                kills_deaths_assists=player_pgcr["values"]["killsDeathsAssists"]["basic"]["value"],
                score=int(player_pgcr["values"]["score"]["basic"]["value"]),
                activity_duration_seconds=int(player_pgcr["values"]["activityDurationSeconds"]["basic"]["value"]),
                completion_reason=int(player_pgcr["values"]["completionReason"]["basic"]["value"]),
                start_seconds=int(player_pgcr["values"]["startSeconds"]["basic"]["value"]),
                time_played_seconds=int(player_pgcr["values"]["timePlayedSeconds"]["basic"]["value"]),
                player_count=int(player_pgcr["values"]["playerCount"]["basic"]["value"]),
                team_score=int(player_pgcr["values"]["teamScore"]["basic"]["value"]),
                precision_kills=int(player_pgcr["extended"]["values"]["precisionKills"]["basic"]["value"]),
                weapon_kills_grenade=int(player_pgcr["extended"]["values"]["weaponKillsGrenade"]["basic"]["value"]),
                weapon_kills_melee=int(player_pgcr["extended"]["values"]["weaponKillsMelee"]["basic"]["value"]),
                weapon_kills_super=int(player_pgcr["extended"]["values"]["weaponKillsSuper"]["basic"]["value"]),
                weapon_kills_ability=int(player_pgcr["extended"]["values"]["weaponKillsAbility"]["basic"]["value"]),
            )

            # loop through the weapons the player used and append that data
            if "weapons" in player_pgcr["extended"]:
                for weapon_pgcr in player_pgcr["extended"]["weapons"]:
                    weapon = ActivitiesUsersWeapons(
                        weapon_id=weapon_pgcr["referenceId"],
                        unique_weapon_kills=int(weapon_pgcr["values"]["uniqueWeaponKills"]["basic"]["value"]),
                        unique_weapon_precision_kills=int(
                            weapon_pgcr["values"]["uniqueWeaponPrecisionKills"]["basic"]["value"]
                        ),
                    )

                    # append weapon data to player
                    to_create.append(weapon)
                    player.weapons.append(weapon)

            # append player data to activity
            to_create.append(player)
            activity.users.append(player)

        # append activity so it also gets inserted
        to_create.append(activity)

        # mass insert all the stuff to the db
        await self._insert_multi(db=db, to_create=to_create)

    async def get_activities(
        self,
        db: AsyncSession,
        destiny_id: int,
        activity_hashes: Optional[list[int]] = None,
        mode: Optional[int] = None,
        no_checkpoints: Optional[bool] = True,
        require_team_flawless: Optional[bool] = None,
        require_individual_flawless: Optional[bool] = None,
        character_class: Optional[str] = None,
        character_ids: Optional[list[int]] = None,
        maximum_allowed_players: Optional[int] = None,
        require_score: Optional[int] = None,
        require_kills: Optional[int] = None,
        require_kills_per_minute: Optional[float] = None,
        require_kda: Optional[float] = None,
        require_kd: Optional[float] = None,
        allow_time_periods: Optional[list[TimePeriodModel]] = None,
        disallow_time_periods: Optional[list[TimePeriodModel]] = None,
    ) -> list[Activities]:
        """Gets a list of all Activities that fulfill the get_requirements"""

        query = select(Activities)

        # filter activity hashes
        if activity_hashes:
            query = query.filter(Activities.director_activity_hash.in_(activity_hashes))

        # filter mode
        if mode:
            query = query.filter(Activities.modes.any(mode))

        # do we accept non checkpoint runs?
        if no_checkpoints:
            query = query.filter(Activities.starting_phase_index == 0)

        query = query.join(Activities.users)
        query = query.group_by(ActivitiesUsers.id)

        # limit max users to player_count
        if maximum_allowed_players:
            query = query.having(func.count(distinct(ActivitiesUsers.destiny_id)) <= maximum_allowed_players)

        # team flawless required?
        if require_team_flawless:
            query = query.having(func.count(distinct(ActivitiesUsers.deaths)) == 0)

        # check completion status
        query = query.filter(ActivitiesUsers.destiny_id == destiny_id)
        query = query.filter(ActivitiesUsers.completed == 1)
        query = query.filter(ActivitiesUsers.completion_reason == 0)

        # individual flawless required?
        if require_individual_flawless:
            query = query.filter(ActivitiesUsers.deaths == 0)

        # limit character class
        if character_class:
            query = query.filter(ActivitiesUsers.character_class == character_class)

        # limit character ids
        if character_ids:
            query = query.filter(ActivitiesUsers.character_id.in_(character_ids))

        # minimum score?
        if require_score:
            query = query.filter(ActivitiesUsers.score > require_score)

        # minimum kills?
        if require_kills:
            query = query.filter(ActivitiesUsers.kills >= require_kills)

        # minimum kills per minute?
        if require_kills_per_minute:
            query = query.filter(
                (ActivitiesUsers.kills * 60 / ActivitiesUsers.time_played_seconds) >= require_kills_per_minute
            )

        # minimum kda?
        if require_kda:
            query = query.filter(ActivitiesUsers.kills_deaths_assists >= require_kda)

        # minimum kd?
        if require_kd:
            query = query.filter(ActivitiesUsers.kills_deaths_ratio >= require_kd)

        # do we have allowed datetimes
        if allow_time_periods:
            for time in allow_time_periods:
                query = query.filter(Activities.period.between(time.start_time, time.end_time))

        # do we have disallowed datetimes
        if disallow_time_periods:
            for time in disallow_time_periods:
                query = query.filter(not_(Activities.period.between(time.start_time, time.end_time)))

        result = await self._execute_query(db=db, query=query)
        return result.scalars().fetchall()

    async def get_last_activity(
        self,
        db: AsyncSession,
        destiny_id: int,
        mode: Optional[int] = None,
        activity_ids: Optional[list[int]] = None,
        completed: bool = True,
        character_class: Optional[str] = None,
    ) -> Optional[Activities]:
        """Gets a list of all Activities that fulfill the get_requirements"""

        query = select(Activities)

        # check mode
        if mode and not activity_ids:
            query = query.filter(Activities.modes.any(mode))

        # check activity_ids
        if activity_ids:
            query = query.filter(Activities.director_activity_hash.in_(activity_ids))

        query = query.join(Activities.users)
        query = query.group_by(ActivitiesUsers.id)

        # filter the destiny id
        query = query.filter(ActivitiesUsers.destiny_id == destiny_id)

        # limit the class
        if character_class:
            query = query.filter(ActivitiesUsers.character_class == character_class)

        # check completion status
        if completed:
            query = query.filter(ActivitiesUsers.completed == 1)

        result = await self._execute_query(db=db, query=query)
        return result.scalar()

    async def calculate_time_played(
        self,
        db: AsyncSession,
        destiny_id: int,
        mode: int = 0,
        activity_ids: Optional[list[int]] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        character_class: Optional[str] = None,
    ) -> int:
        """Calculate the time played (in seconds) from the DB"""

        query = select(func.sum(ActivitiesUsers.time_played_seconds))

        # filter mode
        if mode != 0:
            query = query.filter(ActivitiesUsers.activity.modes.any(mode))

        # filter activities
        if activity_ids:
            query = query.filter(ActivitiesUsers.activity.reference_id.in_(activity_ids))

        # limit to the allowed times if that is requested
        if start_time:
            query = query.filter(ActivitiesUsers.activity.period >= start_time)
        if end_time:
            query = query.filter(ActivitiesUsers.activity.period <= end_time)

        # filter the destiny id
        query = query.filter(ActivitiesUsers.destiny_id == destiny_id)

        # limit the class
        if character_class:
            query = query.filter(ActivitiesUsers.character_class == character_class)

        result = await self._execute_query(db=db, query=query)
        result = result.scalar()

        # I heard this can return None instead of 0, so we're doing this
        return result if result else 0


activities_fail_to_get = CRUDActivitiesFailToGet(ActivitiesFailToGet)
activities = CRUDActivities(Activities)
