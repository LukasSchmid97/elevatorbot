import dataclasses
import datetime
from typing import Any, Optional

from anyio import to_thread
from bungio.models import DamageType, DestinyInventoryItemDefinition, DestinyItemSubType
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.bungio.manifest import destiny_manifest
from Backend.core.errors import CustomException
from Backend.crud import crud_weapons
from Backend.database.models import ActivitiesUsersWeapons, DiscordUsers
from Shared.enums.destiny import DestinyWeaponSlotEnum
from Shared.networkingSchemas.destiny import (
    DestinyTopWeaponModel,
    DestinyTopWeaponsModel,
    DestinyTopWeaponsStatInputModelEnum,
    DestinyWeaponStatsModel,
)


@dataclasses.dataclass
class DestinyWeapons:
    """Clan specific API calls"""

    db: AsyncSession
    user: Optional[DiscordUsers] = None

    def __post_init__(self):
        if self.user:
            # some shortcuts
            self.discord_id = self.user.discord_id
            self.destiny_id = self.user.destiny_id
            self.system = self.user.system

    async def get_weapon_stats(
        self,
        weapon_ids: list[int],
        character_class: Optional[str] = None,
        character_ids: Optional[list[int]] = None,
        mode: Optional[int] = None,
        activity_hashes: Optional[list[int]] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
    ) -> DestinyWeaponStatsModel:
        """
        Return the stats for the given weapon.
        A weapon can have multiple ids, due to sunsetting. That's why the arg is a list
        """

        usages = await crud_weapons.get_usage(
            db=self.db,
            weapon_ids=weapon_ids,
            destiny_id=self.destiny_id,
            character_class=character_class,
            character_ids=character_ids,
            mode=mode,
            activity_hashes=activity_hashes,
            start_time=start_time,
            end_time=end_time,
        )

        # loop through all the usages and find what we are looking for
        result = await to_thread.run_sync(get_weapon_stats_subprocess, usages)

        # change the reference id of the best activity to the actual name
        activity = await destiny_manifest.get_activity(int(result.best_kills_activity_name))
        result.best_kills_activity_name = activity.name

        return result

    async def get_top_weapons(
        self,
        stat: DestinyTopWeaponsStatInputModelEnum,
        how_many_per_slot: Optional[int] = None,
        include_weapon_with_ids: Optional[list[int]] = None,
        weapon_type: Optional[DestinyItemSubType] = None,
        damage_type: Optional[DamageType] = None,
        character_class: Optional[str] = None,
        character_ids: Optional[list[int]] = None,
        mode: Optional[int] = None,
        activity_hashes: Optional[list[int]] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
    ) -> DestinyTopWeaponsModel:
        """
        Return the top x weapons for every slot. include_weapon_with_ids is always included no matter what
        A weapon can have multiple ids, due to sunsetting. That's why the arg is a list
        """

        # get information about the sought weapon
        sought_weapon = None
        if include_weapon_with_ids:
            sought_weapon = await destiny_manifest.get_item(item_id=include_weapon_with_ids[0])

            # check if the weapon / damage type matches
            if weapon_type and sought_weapon.item_sub_type != weapon_type.value:
                raise CustomException("WeaponTypeMismatch")
            if damage_type and sought_weapon.default_damage_type != damage_type.value:
                raise CustomException("WeaponDamageTypeMismatch")

        # loop through all three slots
        result = DestinyTopWeaponsModel()
        for slot in DestinyWeaponSlotEnum:
            # query the db
            top_weapons = await crud_weapons.get_top(
                db=self.db,
                slot=slot,
                stat=stat,
                destiny_id=self.destiny_id,
                weapon_type=weapon_type,
                damage_type=damage_type,
                character_class=character_class,
                character_ids=character_ids,
                mode=mode,
                activity_hashes=activity_hashes,
                start_time=start_time,
                end_time=end_time,
            )

            # get the weapon definitions
            top_weapons_weapons = [
                await destiny_manifest.get_weapon(weapon_id=weapon_data.weapon_id) for weapon_data in top_weapons
            ]

            sorted_slot = await to_thread.run_sync(
                lambda: get_top_weapons_subprocess(
                    top_weapons=top_weapons,
                    top_weapons_weapons=top_weapons_weapons,
                    stat=stat,
                    sought_weapon=sought_weapon,
                    slot=slot,
                    how_many_per_slot=how_many_per_slot,
                    include_weapon_with_ids=include_weapon_with_ids,
                )
            )

            # update the result
            setattr(result, slot.name.lower(), sorted_slot)

        return result


def get_weapon_stats_subprocess(usages: list[ActivitiesUsersWeapons]) -> DestinyWeaponStatsModel:
    """Run in anyio subprocess on another thread since this might be slow"""

    result = DestinyWeaponStatsModel(
        total_kills=0,
        total_precision_kills=0,
        total_activities=0,
        best_kills=0,
        best_kills_activity_name="",
        best_kills_activity_id=0,
        best_kills_date=datetime.datetime.min,
    )

    if not usages:
        raise CustomException("WeaponUnused")

    for usage in usages:
        result.total_kills += usage.unique_weapon_kills
        result.total_precision_kills += usage.unique_weapon_precision_kills
        result.total_activities += 1

        if usage.unique_weapon_kills > result.best_kills:
            result.best_kills = usage.unique_weapon_kills
            result.best_kills_activity_name = str(usage.user.activity.reference_id)
            result.best_kills_activity_id = usage.user.activity.instance_id
            result.best_kills_date = usage.user.activity.period

    return result


def get_top_weapons_subprocess(
    top_weapons: list[Row],
    top_weapons_weapons: list[DestinyInventoryItemDefinition],
    stat: DestinyTopWeaponsStatInputModelEnum,
    sought_weapon: Optional[DestinyInventoryItemDefinition],
    slot: Any,
    how_many_per_slot: Optional[int],
    include_weapon_with_ids: Optional[list[int]],
) -> list[DestinyTopWeaponModel]:
    """Run in anyio subprocess on another thread since this might be slow"""

    # sort the weapons. This is needed because some weapons are reissued and have multiple ids
    to_sort = {}
    for weapon_data, weapon in zip(top_weapons, top_weapons_weapons):
        # get the stat value
        stat_value = getattr(weapon_data, stat.name.lower())

        # insert into the sorting thing
        if weapon.display_properties.name not in to_sort:
            to_sort.update(
                {
                    weapon.display_properties.name: DestinyTopWeaponModel(
                        ranking=0,  # temp value
                        stat_value=stat_value,
                        weapon_ids=[weapon.hash],
                        weapon_name=weapon.display_properties.name,
                        weapon_type=weapon.item_sub_type.display_name,
                        weapon_tier=weapon.inventory.tier_type_name,
                        weapon_damage_type=weapon.default_damage_type.display_name,
                        weapon_ammo_type=weapon.equipping_block.ammo_type.display_name,
                    )
                }
            )

        # append the id and add the stat
        else:
            to_sort[weapon.display_properties.name].stat_value += stat_value
            to_sort[weapon.display_properties.name].weapon_ids.append(weapon.hash)

    # sort the items
    sorted_slot: list[DestinyTopWeaponModel] = sorted(
        to_sort.values(), key=lambda entry: entry.stat_value, reverse=True
    )

    # set the rankings and the limit and include the sought weapon
    found = sought_weapon.bucket_type_hash != slot.value if sought_weapon else True
    final_slot = []
    for i, item in enumerate(sorted_slot):
        if not how_many_per_slot or i < how_many_per_slot:
            item.ranking = i + 1
            final_slot.append(item)

            if sought_weapon and include_weapon_with_ids[0] in item.weapon_ids:
                found = True

        elif not found:
            if sought_weapon and sought_weapon.reference_id in item.weapon_ids:
                item.ranking = i + 1
                final_slot.append(item)
                found = True

        else:
            break

    # raise an error since the weapon wasn't found
    if not found:
        raise CustomException("WeaponUnused")

    return sorted_slot
