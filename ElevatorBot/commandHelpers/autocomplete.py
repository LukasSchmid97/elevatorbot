from dis_snek.models import AutocompleteContext
from rapidfuzz import fuzz, process

from NetworkingSchemas.destiny.activities import DestinyActivityModel
from NetworkingSchemas.destiny.weapons import DestinyWeaponModel

# all activities are in here at runtime
activities_grandmaster: dict[str, DestinyActivityModel] = {}
activities: dict[str, DestinyActivityModel] = {}
activities_by_id: dict[int, DestinyActivityModel] = {}

# all weapons are in here at runtime
weapons: dict[str, DestinyWeaponModel] = {}
weapons_by_id: dict[int, DestinyWeaponModel] = {}


async def autocomplete_send_activity_name(ctx: AutocompleteContext, activity: str):
    """Send the user the best fitting activities (fuzzy)"""

    best_matches = process.extract(activity.lower(), list(activities), scorer=fuzz.WRatio, limit=25)
    await ctx.send(
        choices=[
            {
                "name": activities[match[0]].name,
                "value": activities[match[0]].name,
            }
            for match in best_matches
        ]
    )


async def autocomplete_send_weapon_name(ctx: AutocompleteContext, weapon: str):
    """Send the user the best fitting weapons (fuzzy)"""

    best_matches = process.extract(weapon.lower(), list(weapons), scorer=fuzz.WRatio, limit=25)
    await ctx.send(
        choices=[
            {
                "name": weapons[match[0]].name,
                "value": weapons[match[0]].name,
            }
            for match in best_matches
        ]
    )
