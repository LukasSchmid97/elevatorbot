from dis_snek.client import Snake

from DestinyEnums.enums import DestinyActivityModeTypeEnum
from ElevatorBot.backendNetworking.destiny.activities import DestinyActivities
from ElevatorBot.backendNetworking.destiny.weapons import DestinyWeapons
from ElevatorBot.commandHelpers.autocomplete import (
    activities,
    activities_by_id,
    activities_grandmaster,
    weapons,
    weapons_by_id,
)

# todo redo those on manifest update
from NetworkingSchemas.destiny.activities import DestinyActivityModel


async def load_autocomplete_options(client: Snake):
    """Fetch the needed data from the DB"""

    # get activities
    # loop through them all and add them to the global activities dict
    backend = DestinyActivities(ctx=None, discord_member=None, client=None, discord_guild=None)
    db_activities = await backend.get_all()
    if not db_activities:
        raise LookupError("Couldn't load activities")

    raids = []
    dungeons = []
    for activity in db_activities.activities:
        # save the raids
        if activity.mode == DestinyActivityModeTypeEnum.RAID.value:
            for activity_id in activity.activity_ids:
                raids.append(activity_id)

        # save the dungeons
        if activity.mode == DestinyActivityModeTypeEnum.DUNGEON.value:
            for activity_id in activity.activity_ids:
                dungeons.append(activity_id)

        # don't add the budget grandmasters
        if "Grandmaster" not in activity.name:
            activities.update({activity.name.lower(): activity})
            for activity_id in activity.activity_ids:
                activities_by_id.update({activity_id: activity})

    # get the more nicely formatted gms
    db_grandmaster = await backend.get_grandmaster()
    if not db_grandmaster:
        raise LookupError("Couldn't load grandmasters")

    # get all raids
    activities.update(
        {
            "Raid: All": DestinyActivityModel(
                name="Raid: All",
                description="Raid: All",
                activity_ids=raids,
                mode=DestinyActivityModeTypeEnum.RAID.value,
            )
        }
    )

    # get all dungeons
    activities.update(
        {
            "Dungeon: All": DestinyActivityModel(
                name="Dungeon: All",
                description="Dungeon: All",
                activity_ids=dungeons,
                mode=DestinyActivityModeTypeEnum.DUNGEON.value,
            )
        }
    )

    for grandmaster in db_grandmaster.activities:
        activities_grandmaster.update({grandmaster.name.lower(): grandmaster})
        activities.update({grandmaster.name.lower(): grandmaster})
        for activity_id in grandmaster.activity_ids:
            activities_by_id.update({activity_id: grandmaster})

    # get weapons
    db_weapons = await DestinyWeapons(ctx=None, discord_member=None, client=None, discord_guild=None).get_all()
    if not db_activities:
        raise LookupError("Couldn't load weapons")

    for weapon in db_weapons.weapons:
        weapons.update({weapon.name.lower(): weapon})
        for reference_id in weapon.reference_ids:
            weapons_by_id.update({reference_id: weapon})
