import dataclasses
from typing import Optional

from dis_snek.client import Snake
from dis_snek.models import Role
from dis_snek.models.context import InteractionContext
from dis_snek.models.discord_objects.guild import Guild
from dis_snek.models.discord_objects.user import Member

from ElevatorBot.backendNetworking.destiny.roles import DestinyRoles
from ElevatorBot.commandHelpers.autocomplete import activities_by_id
from ElevatorBot.misc.cache import collectible_cache, triumph_cache
from ElevatorBot.misc.formating import embed_message


@dataclasses.dataclass()
class Roles:
    """Class to handle achievement Roles"""

    client: Snake
    guild: Guild
    member: Member
    ctx: Optional[InteractionContext]

    def __post_init__(self):
        self.roles = DestinyRoles(
            ctx=self.ctx, client=self.client, discord_guild=self.guild, discord_member=self.member
        )

    async def get_requirements(self, role: Role):
        """Get a roles get_requirements and what user has done"""

        # get info what get_requirements the user fulfills and which not and info on the role
        result = await self.roles.get_detail(role)

        if not result:
            return

        role_data = result.role_data
        user_data = result.user_data

        # construct reply msg
        embed = embed_message(
            f"{self.member.display_name}'s '{role.name}' Eligibility", f"""**Earned: {result.earned}**"""
        )

        # loop through the requirements and their statuses
        activities: list[str] = []
        collectibles: list[str] = []
        records: list[str] = []
        roles: list[str] = []
        for role_info, user_info in zip(role_data, user_data):
            match role_info:
                case "require_activity_completions":
                    for role_activity, user_activity in zip(
                        role_data[role_info].values(), user_data[role_info].values()
                    ):
                        activities.append(f"{activities_by_id[role_activity].name}: {user_activity}")

                case "require_collectibles":
                    for role_collectible, user_collectible in zip(
                        role_data[role_info].values(), user_data[role_info].values()
                    ):
                        collectibles.append(
                            f"[{await collectible_cache.get_name(collectible_id=role_collectible)}](https://www.light.gg/db/items/{role_collectible}): {user_collectible}"
                        )

                case "require_records":
                    for role_record, user_record in zip(role_data[role_info].values(), user_data[role_info].values()):
                        records.append(
                            f"[{await triumph_cache.get_name(triumph_cache=role_record)}](https://www.light.gg/db/legend/triumphs/{role_record}): {user_record}"
                        )

                case "require_role_ids":
                    for role_role_id, user_role_id in zip(role_data[role_info].values(), user_data[role_info].values()):
                        roles.append(f"{(await self.guild.get_role(role_role_id)).mention}: {user_role_id}")

        # add the embed fields
        if activities:
            embed.add_field(name="Required Activity Completions", value="\n".join(activities), inline=False)
        if collectibles:
            embed.add_field(name="Required Collectibles", value="\n".join(collectibles), inline=False)
        if records:
            embed.add_field(name="Required Triumphs", value="\n".join(records), inline=False)
        if roles:
            embed.add_field(name="Required Roles", value="\n".join(roles), inline=False)

        await self.ctx.send(embeds=embed)

    async def get_missing(self):
        """Get a members missing roles"""

        result = await self.roles.get_missing()

        if not result:
            return

        acquirable_roles: dict[str, list[int]] = result.acquirable
        deprecated_roles: dict[str, list[int]] = result.deprecated

        # do the missing roles display
        embed = embed_message(f"{self.member.display_name}'s Roles")
        embed.add_field(name="⁣", value=f"__**Acquirable Roles:**__", inline=False)

        # only do this if there are roles to get
        if acquirable_roles:
            for category, role_ids in acquirable_roles.items():
                embed.add_field(
                    name=category,
                    value=("\n".join([(await self.guild.get_role(role_id)).mention for role_id in role_ids]) or "None"),
                    inline=True,
                )
        else:
            embed.add_field(
                name="Wow, you got every single role. Congrats!",
                value="⁣",
                inline=False,
            )

        # Do the same for the deprecated roles
        embed.add_field(name="⁣", value=f"__**Deprecated Roles:**__", inline=False)
        if deprecated_roles:
            for category, role_ids in deprecated_roles.items():
                embed.add_field(
                    name=category,
                    value="\n".join([(await self.guild.get_role(role_id)).mention for role_id in role_ids]),
                    inline=True,
                )

        await self.ctx.send(embeds=embed)

    async def update(self):
        """Get and update a members roles"""

        result = await self.roles.get()

        if not result:
            return

        roles_at_start = [role.id for role in self.ctx.author.roles]

        earned_roles: dict[str, list[int]] = result.earned
        earned_but_replaced_by_higher_role_roles: dict[str, list[int]] = result.earned_but_replaced_by_higher_role
        not_earned_roles: dict[str, list[int]] = result.not_earned

        # assign new roles
        for category in earned_roles.values():
            for role_id in category:
                await self.member.add_role(role=role_id)

        # remove old roles
        for category in earned_but_replaced_by_higher_role_roles.values():
            for role_id in category:
                await self.member.remove_role(role=role_id)
        for category in not_earned_roles.values():
            for role_id in category:
                await self.member.remove_role(role=role_id)

        # send a message
        if self.ctx:
            # if user has no roles show this
            if not earned_roles:
                await self.ctx.send(
                    # todo link to where you can see all the roles
                    embeds=embed_message(
                        "Info",
                        f"You don't have any roles. \nUse `/roles overview` to see all available roles and then `/roles get_requirements <role>` to view its get_requirements.",
                    )
                )
                return

            all_earned_roles = self._get_all_earned_roles(earned_roles, earned_but_replaced_by_higher_role_roles)

            # now separate into newly earned roles and the old ones
            old_roles = {}
            new_roles = {}
            for category, role_ids in all_earned_roles.items():
                for role_id in role_ids:
                    discord_role = await self.guild.get_role(role_id)

                    if discord_role:
                        # check if they had the role
                        if discord_role.id in roles_at_start:
                            if category not in old_roles:
                                old_roles.update({category: []})
                            old_roles[category].append(discord_role.mention)

                        else:
                            if category not in new_roles:
                                new_roles.update({category: []})
                            new_roles[category].append(discord_role.mention)

            # construct reply msg
            embed = embed_message(f"{self.member.display_name}'s new Roles", f"__Previous Roles:__")
            if not old_roles:
                embed.add_field(name=f"You didn't have any roles before", value="⁣", inline=True)

            for topic in old_roles:
                roles = []
                for role_name in topic:
                    roles.append(role_name)
                embed.add_field(name=topic, value="\n".join(old_roles[topic]), inline=True)

            embed.add_field(name="⁣", value=f"__New Roles:__", inline=False)
            if not new_roles:
                embed.add_field(name="No new roles have been achieved", value="⁣", inline=True)

            for topic in new_roles:
                roles = []
                for role_name in topic:
                    roles.append(role_name)
                embed.add_field(name=topic, value="\n".join(new_roles[topic]), inline=True)

            await self.ctx.send(embeds=embed)

    @staticmethod
    def _get_all_earned_roles(earned_roles: dict, earned_but_replaced_by_higher_role_roles: dict) -> dict:
        """Combine earned_roles and earned_but_replaced_by_higher_role_roles"""

        all_earned_roles = earned_roles.copy()
        for category, role_ids in earned_but_replaced_by_higher_role_roles.items():
            for role_id in role_ids:
                if category not in all_earned_roles:
                    all_earned_roles.update({category: []})
                all_earned_roles[category].append(role_id)

        return all_earned_roles
