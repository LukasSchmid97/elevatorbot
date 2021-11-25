from dis_snek.models import (
    InteractionContext,
    Member,
    OptionTypes,
    SlashCommandChoice,
    Timestamp,
    TimestampStyles,
    slash_command,
    slash_option,
)

from DestinyEnums.enums import (
    DestinyWeaponTypeEnum,
    UsableDestinyActivityModeTypeEnum,
    UsableDestinyDamageTypeEnum,
)
from ElevatorBot.backendNetworking.destiny.weapons import DestinyWeapons
from ElevatorBot.commandHelpers.autocomplete import activities, weapons
from ElevatorBot.commandHelpers.optionTemplates import (
    autocomplete_activity_option,
    autocomplete_weapon_option,
    default_class_option,
    default_damage_type_option,
    default_expansion_option,
    default_mode_option,
    default_season_option,
    default_time_option,
    default_user_option,
    default_weapon_type_option,
)
from ElevatorBot.commandHelpers.subCommandTemplates import weapons_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import capitalize_string, embed_message
from ElevatorBot.misc.helperFunctions import parse_datetime_options
from ElevatorBot.static.emojis import custom_emojis
from NetworkingSchemas.destiny.weapons import (
    DestinyTopWeaponModel,
    DestinyTopWeaponsInputModel,
    DestinyTopWeaponsStatInputModelEnum,
)


class WeaponsTop(BaseScale):
    """
    Shows your top Destiny 2 weapon ranking

    :option:weapon: If you want a specific weapon to be included in the ranking. Otherwise the command will only show your top eight weapons per slot
    """

    @slash_command(
        **weapons_sub_command, sub_cmd_name="top", sub_cmd_description="Shows your top Destiny 2 weapon ranking"
    )
    @slash_option(
        name="stat",
        description="Which stat you want the leaderboard to consider. Default: Kills",
        required=False,
        opt_type=OptionTypes.STRING,
        choices=[
            SlashCommandChoice(name="Kills", value="kills"),
            SlashCommandChoice(name="Precision Kills", value="precision_kills"),
        ],
    )
    @autocomplete_weapon_option(description="If you want a specific weapon to be included in the ranking")
    @default_mode_option()
    @autocomplete_activity_option()
    @default_weapon_type_option()
    @default_damage_type_option()
    @default_class_option()
    @default_expansion_option()
    @default_season_option()
    @default_time_option(
        name="start_time",
        description="Format: `DD/MM/YY` - Input the **earliest** date you want the weapon stats for. Default: Big Bang",
    )
    @default_time_option(
        name="end_time",
        description="Format: `DD/MM/YY` - Input the **latest** date you want the weapon stats for. Default: Now",
    )
    @default_user_option()
    async def _top_weapons(
        self,
        ctx: InteractionContext,
        stat: str = "kills",
        weapon: str = None,
        mode: str = None,
        activity: str = None,
        destiny_class: str = None,
        weapon_type: int = None,
        damage_type: int = None,
        expansion: str = None,
        season: str = None,
        start_time: str = None,
        end_time: str = None,
        user: Member = None,
    ):
        mode = int(mode) if mode else None

        limit = 8
        stat = (
            DestinyTopWeaponsStatInputModelEnum.KILLS
            if stat == "kills"
            else DestinyTopWeaponsStatInputModelEnum.PRECISION_KILLS
        )

        # parse start and end time
        start_time, end_time = parse_datetime_options(
            ctx=ctx, expansion=expansion, season=season, start_time=start_time, end_time=end_time
        )
        if not start_time:
            return

        # get the actual weapon / activities
        if weapon:
            weapon = weapons[weapon.lower()]
        if activity:
            activity = activities[activity.lower()]

        # might take a sec
        await ctx.defer()

        member = user or ctx.author
        backend_weapons = DestinyWeapons(ctx=ctx, client=ctx.bot, discord_member=member, discord_guild=ctx.guild)

        # get the top weapons
        stats = await backend_weapons.get_top(
            input_data=DestinyTopWeaponsInputModel(
                stat=stat,
                how_many_per_slot=limit,
                include_weapon_with_ids=weapon.reference_ids if weapon else None,
                weapon_type=weapon_type,
                damage_type=damage_type,
                character_class=destiny_class,
                mode=mode,
                activity_hashes=activity.activity_ids if activity else None,
                start_time=start_time,
                end_time=end_time,
            )
        )

        if not stats:
            return

        # format the message
        embed = embed_message(
            f"{member.display_name}'s Top Weapons",
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
        for entry in stats:
            slot_name = entry[0]
            slot_entries: list[DestinyTopWeaponModel] = getattr(stats, slot_name)

            field_text = []
            for item in slot_entries:
                # append the ... if the sought weapon is in here
                if weapon and len(slot_entries) > limit:
                    if len(field_text) == limit:
                        field_text.append("...")

                if weapon and weapon.reference_ids[0] in item.weapon_ids:
                    field_text.append(
                        f"""**{item.ranking}) {getattr(custom_emojis, item.weapon_type.lower())}{getattr(custom_emojis, item.weapon_damage_type.lower())}{getattr(custom_emojis, item.weapon_ammo_type.lower())} [{item.weapon_name}](https://www.light.gg/db/items/{item.weapon_ids[0]})\n{custom_emojis.enter} {capitalize_string(stat.name)}: {item.stat_value}**"""
                    )
                else:
                    field_text.append(
                        f"""{item.ranking}) {getattr(custom_emojis, item.weapon_type.lower())}{getattr(custom_emojis, item.weapon_damage_type.lower())}{getattr(custom_emojis, item.weapon_ammo_type.lower())} [{item.weapon_name}](https://www.light.gg/db/items/{item.weapon_ids[0]})\n{custom_emojis.enter} {capitalize_string(stat.name)}: {item.stat_value}"""
                    )

            embed.add_field(name=slot_name, value="\n".join(field_text) or "None", inline=True)

        await ctx.send(embeds=embed)


def setup(client):
    WeaponsTop(client)
