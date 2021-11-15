import asyncio
import datetime
from typing import Optional

from dis_snek.models import (
    Guild,
    InteractionContext,
    Timestamp,
    TimestampStyles,
    slash_command,
)

from DestinyEnums.enums import (
    DestinyWeaponTypeEnum,
    UsableDestinyActivityModeTypeEnum,
    UsableDestinyDamageTypeEnum,
)
from ElevatorBot.backendNetworking.destiny.clan import DestinyClan
from ElevatorBot.backendNetworking.destiny.weapons import DestinyWeapons
from ElevatorBot.commandHelpers.autocomplete import activities
from ElevatorBot.commandHelpers.optionTemplates import (
    autocomplete_activity_option,
    default_class_option,
    default_damage_type_option,
    default_expansion_option,
    default_mode_option,
    default_season_option,
    default_time_option,
    default_weapon_type_option,
)
from ElevatorBot.commandHelpers.responseTemplates import something_went_wrong
from ElevatorBot.commandHelpers.subCommandTemplates import weapons_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import capitalize_string, embed_message
from ElevatorBot.misc.helperFunctions import parse_datetime_options
from ElevatorBot.static.emojis import custom_emojis
from NetworkingSchemas.destiny.activities import DestinyActivityModel
from NetworkingSchemas.destiny.weapons import (
    DestinyTopWeaponModel,
    DestinyTopWeaponsInputModel,
    DestinyTopWeaponsModel,
    DestinyTopWeaponsStatInputModelEnum,
)


class WeaponsMeta(BaseScale):
    @slash_command(
        **weapons_sub_command,
        sub_cmd_name="meta",
        sub_cmd_description="Displays most used weapons by clan members in the linked clan",
    )
    @default_mode_option(description="Restrict the game mode where the weapon stats count. Default: All modes")
    @autocomplete_activity_option(
        description="Restrict the activity where the weapon stats count. Overwrites `mode`. Default: All modes"
    )
    @default_weapon_type_option(description="Restrict the weapon type is looked at. Default: All types")
    @default_damage_type_option(description="Restrict the damage type which are looked at. Default: All types")
    @default_class_option(description="Restrict the class where the weapon stats count. Default: All classes")
    @default_expansion_option(description="Restrict the expansion where the weapon stats count")
    @default_season_option(description="Restrict the season where the weapon stats count")
    @default_time_option(
        name="start_time",
        description="Format: `DD/MM/YY` - Input the **earliest** date you want the weapon stats for. Default: Big Bang",
    )
    @default_time_option(
        name="end_time",
        description="Format: `DD/MM/YY` - Input the **latest** date you want the weapon stats for. Default: Now",
    )
    async def _meta(
        self,
        ctx: InteractionContext,
        mode: int = None,
        activity: str = None,
        destiny_class: str = None,
        weapon_type: int = None,
        damage_type: int = None,
        expansion: str = None,
        season: str = None,
        start_time: str = None,
        end_time: str = None,
    ):
        limit = 8
        stat = DestinyTopWeaponsStatInputModelEnum.KILLS

        # get the linked clan member
        clan = DestinyClan(client=ctx.bot, discord_guild=ctx.guild, discord_member=ctx.author, ctx=ctx)
        clan_info = await clan.get_clan()
        if not clan_info:
            return
        clan_members = await clan.get_clan_members()
        if not clan_members:
            return

        # parse start and end time
        start_time, end_time = parse_datetime_options(
            ctx=ctx, expansion=expansion, season=season, start_time=start_time, end_time=end_time
        )
        if not start_time:
            return

        # get the actual activity
        if activity:
            activity = activities[activity.lower()]

        # might take a sec
        await ctx.defer()

        # gather the clan members
        results = await asyncio.gather(
            *[
                self.handle_clan_member(
                    stat=stat,
                    guild=ctx.guild,
                    discord_id=clan_member.discord_id,
                    start_time=start_time,
                    end_time=end_time,
                    mode=mode,
                    activity=activity,
                    destiny_class=destiny_class,
                    weapon_type=weapon_type,
                    damage_type=damage_type,
                )
                for clan_member in clan_members.members
            ]
        )

        # fail is something went wrong
        if any([not result for result in results]):
            await something_went_wrong(ctx=ctx)
            return

        # loop through the results and combine the weapon stats
        to_sort = {}
        for result in results:
            for entry in result:
                slot_name = entry[0]
                slot_entries: list[DestinyTopWeaponModel] = getattr(result, slot_name)

                if slot_name not in to_sort:
                    to_sort.update({slot_name: {}})

                for item in slot_entries:
                    if item.weapon_name not in to_sort[slot_name]:
                        to_sort[slot_name].update({item.weapon_name: item})

                    # add the stats
                    else:
                        to_sort[slot_name][item.weapon_name].stat_value += item.stat_value

        # sort that
        sorted_slot = {}
        for slot_name, data in to_sort:
            sorted_data: list[DestinyTopWeaponModel] = sorted(data, key=lambda weapon: weapon.stat_value, reverse=True)

            sorted_slot.update({slot_name: sorted_data[:limit]})

        # format the message
        embed = embed_message(
            f"{clan_info.name}'s Weapon Meta",
            f"Date: {Timestamp.fromdatetime(start_time).format(style=TimestampStyles.ShortDateTime)} - {Timestamp.fromdatetime(end_time).format(style=TimestampStyles.ShortDateTime)}",
        )
        if weapon_type:
            embed.description += f"\nWeapon Type: {getattr(custom_emojis, DestinyWeaponTypeEnum(weapon_type).name.lower())} {capitalize_string(DestinyWeaponTypeEnum(weapon_type).name)}"
        if damage_type:
            embed.description += f"\nDamage Type: {getattr(custom_emojis, UsableDestinyDamageTypeEnum(damage_type).name.lower())} {capitalize_string(UsableDestinyDamageTypeEnum(damage_type).name)}"

        # set the footer
        footer = []
        if mode:
            footer.append(f"Mode: {capitalize_string(UsableDestinyActivityModeTypeEnum(mode).name)}")
        if activity:
            footer.append(f"Activity: {activity.name}")
        if destiny_class:
            footer.append(f"Class: {getattr(custom_emojis, destiny_class.lower())} {destiny_class}")
        if footer:
            embed.set_footer(" | ".join(footer))

        # add the fields to the embed
        for i, (slot_name, data) in enumerate(sorted_slot.items()):
            field_text = []
            for item in data:
                field_text.append(
                    f"""{i + 1}) {getattr(custom_emojis, item.weapon_type.lower())}{getattr(custom_emojis, item.weapon_damage_type.lower())}{getattr(custom_emojis, item.weapon_ammo_type.lower())} [{item.weapon_name}](https://www.light.gg/db/items/{item.weapon_ids[0]})\n{custom_emojis.enter} {capitalize_string(stat.name)}: {item.stat_value}"""
                )

            embed.add_field(name=slot_name, value="\n".join(field_text) or "None", inline=True)

        await ctx.send(embeds=embed)

    async def handle_clan_member(
        self,
        stat: DestinyTopWeaponsStatInputModelEnum,
        discord_id: int,
        guild: Guild,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        mode: int = None,
        activity: DestinyActivityModel = None,
        destiny_class: str = None,
        weapon_type: int = None,
        damage_type: int = None,
    ) -> Optional[DestinyTopWeaponsModel]:
        """Gather all clan members. Return None if something fails"""

        # get the top weapons for the user
        backend_weapons = DestinyWeapons(ctx=None, client=self.client, discord_member=None, discord_guild=guild)
        return await backend_weapons.get_top(
            discord_id=discord_id,
            input_data=DestinyTopWeaponsInputModel(
                stat=stat,
                weapon_type=weapon_type,
                damage_type=damage_type,
                character_class=destiny_class,
                mode=mode,
                activity_hashes=activity.activity_ids if activity else None,
                start_time=start_time,
                end_time=end_time,
            ),
        )


def setup(client):
    WeaponsMeta(client)
