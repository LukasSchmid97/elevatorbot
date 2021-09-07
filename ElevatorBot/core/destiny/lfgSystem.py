from __future__ import annotations

import asyncio
import dataclasses
import datetime
from typing import Optional

import discord
from apscheduler.jobstores.base import JobLookupError
from discord_slash import SlashContext, ComponentContext, ButtonStyle
from discord_slash.utils import manage_components

from ElevatorBot.backendNetworking.destiny.lfgSystem import DestinyLfgSystem
from ElevatorBot.backendNetworking.results import BackendResult
from ElevatorBot.backgroundEvents import scheduler
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.misc.helperFunctions import get_now_with_tz
from ElevatorBot.static.emojis import backup_emoji_id, join_emoji_id, leave_emoji_id
from ElevatorBot.static.schemas import LfgInputData, LfgUpdateData


@dataclasses.dataclass()
class LfgMessage:
    """Class to hold an LFG message"""

    backend: DestinyLfgSystem

    client: discord.Client
    id: int

    guild: discord.Guild
    channel: discord.TextChannel

    author: discord.Member
    activity: str
    description: str
    start_time: datetime.datetime
    max_joined_members: int

    message: discord.Message = None
    creation_time: datetime.datetime = None
    joined: list[discord.Member] = None
    backup: list[discord.Member] = dataclasses.field(default_factory=list)

    voice_category_channel: discord.CategoryChannel = None
    voice_channel: discord.VoiceChannel = None

    # post init to do list
    def __post_init__(self):
        # get the scheduler object
        self.scheduler = scheduler

        # get the button emojis
        self.__join_emoji = self.client.get_emoji(join_emoji_id)
        self.__leave_emoji = self.client.get_emoji(leave_emoji_id)
        self.__backup_emoji = self.client.get_emoji(backup_emoji_id)

        # buttons
        self.__buttons = [
            manage_components.create_actionrow(
                manage_components.create_button(custom_id="lfg_join", style=ButtonStyle.green, label="Join"),
                manage_components.create_button(custom_id="lfg_leave", style=ButtonStyle.red, label="Leave"),
                manage_components.create_button(custom_id="lfg_backup", style=ButtonStyle.blue, label="Backup"),
            ),
        ]

    # less than operator to sort the classes by their start time
    def __lt__(self, other):
        return self.start_time < other.start_time

    def __bool__(self):
        return True

    @classmethod
    async def from_lfg_id(cls, lfg_id: int, client: discord.Client, guild: discord.Guild) -> LfgMessage | BackendResult:
        """
        Classmethod to get with a known lfg_id
        Returns LfgMessage() if successful, BackendResult() if not
        """

        backend = DestinyLfgSystem(client=client, discord_guild=guild)

        # get the message by the id
        result = await backend.get(lfg_id=lfg_id)
        if not result:
            return result

        # fill class info
        channel: discord.TextChannel = guild.get_channel(result.result["channel_id"])
        lfg_message = cls(
            backend=backend,
            client=client,
            id=result.result["id"],
            guild=guild,
            channel=channel,
            author=guild.get_member(result.result["author_id"]),
            activity=result.result["activity"],
            description=result.result["description"],
            start_time=result.result["start_time"],
            max_joined_members=result.result["max_joined_members"],
            message=await channel.fetch_message(result.result["message_id"]),
            creation_time=result.result["creation_time"],
            joined=[guild.get_member(member_id) for member_id in result.result["joined_members"]],
            backup=[guild.get_member(member_id) for member_id in result.result["alternate_members"]],
            voice_channel=guild.get_channel(result.result["voice_channel_id"]),
            voice_category_channel=guild.get_channel(result.result["voice_category_channel_id"])
        )

        return lfg_message

    @classmethod
    async def create(
        cls, ctx: SlashContext, activity: str, description: str, start_time: datetime.datetime, max_joined_members: int
    ) -> Optional[LfgMessage]:
        """Classmethod to create a new lfg message"""

        backend = DestinyLfgSystem(client=ctx.bot, discord_guild=ctx.guild)

        # create the message and fill it later
        result = await backend.create(
            discord_member=ctx.author,
            lfg_data=LfgInputData(
                activity=activity,
                description=description,
                start_time=start_time,
                max_joined_members=max_joined_members,
                joined_members=[ctx.author.id],
                alternate_members=[],
            ),
        )

        # error out if need be
        if not result:
            await result.send_error_message(ctx)
            return

        # create class obj
        lfg_message = cls(
            backend=backend,
            client=ctx.bot,
            id=result.result["id"],
            guild=ctx.guild,
            channel=ctx.guild.get_channel(result.result["channel_id"]),
            author=ctx.author,
            activity=activity,
            description=description,
            start_time=start_time,
            max_joined_members=max_joined_members,
            voice_category_channel=ctx.guild.get_channel(result.result["voice_category_channel_id"])
        )

        # send message in the channel to populate missing entries
        await lfg_message.send()

        # respond to the context
        await ctx.send(embed=embed_message("Success", f"I've created the event \nIt has the ID `{lfg_message.id}`"))

        return lfg_message

    async def add_joined(
        self,
        member: discord.Member,
        ctx: ComponentContext = None,
        force_into_joined: bool = False,
    ) -> bool:
        """add a member"""

        if member not in self.joined:
            if (len(self.joined) < self.max_joined_members) or force_into_joined:
                self.joined.append(member)
                if member in self.backup:
                    self.backup.remove(member)
            else:
                if member not in self.backup:
                    self.backup.append(member)
                else:
                    return False

            await self.send(ctx=ctx)
            return True
        return False

    async def add_backup(self, member: discord.Member, ctx: ComponentContext = None) -> bool:
        """add a backup or move member to backup"""

        if member not in self.backup:
            self.backup.append(member)

            if member in self.joined:
                self.joined.remove(member)

            await self.send(ctx=ctx)
            return True
        return False

    async def remove_member(self, member: discord.Member, ctx: ComponentContext = None) -> bool:
        """delete a member"""

        if member in self.joined:
            self.joined.remove(member)

            await self.send(ctx=ctx)
            return True

        elif member in self.backup:
            self.backup.remove(member)

            await self.send(ctx=ctx)
            return True
        return False

    async def notify_about_start(self, time_to_start: datetime.timedelta):
        """notifies joined members that the event is about to start"""

        voice_text = "Please start gathering in a voice channel"

        # get the voice channel category and make a voice channel
        if self.voice_category_channel:
            voice_channel_name = f"[ID: {self.id}] {self.activity}"

            # allow each participant to move members
            permission_overrides = {}
            for member in self.joined:
                # allow the author to also mute
                if member == self.author:
                    permission_overrides.update(
                        {
                            member: discord.PermissionOverwrite(
                                move_members=True,
                                mute_members=True,
                            )
                        }
                    )
                else:
                    permission_overrides.update(
                        {
                            member: discord.PermissionOverwrite(
                                move_members=True,
                            )
                        }
                    )

            self.voice_channel = await self.voice_category_channel.create_voice_channel(
                name=voice_channel_name,
                bitrate=self.guild.bitrate_limit,
                user_limit=self.max_joined_members,
                overwrites=permission_overrides,
                reason="LFG event starting",
            )

            # make fancy text
            voice_text = f"Click here to join the voice channel -> {self.voice_channel.mention}"

        # prepare embed
        embed = embed_message(
            f"LFG Event - {self.activity}",
            f"The LFG event with the ID `{self.id}` is going to start in **{int(time_to_start.seconds / 60)} minutes**\n{voice_text}",
            "Start Time",
        )
        embed.add_field(
            name="Guardians",
            value=", ".join(self.__get_joined_members_display_names()),
            inline=False,
        )
        embed.timestamp = self.start_time

        # if the event was not full
        missing = self.max_joined_members - len(self.joined)
        if self.backup:
            embed.add_field(
                name="Backup",
                value=", ".join(self.__get_alternate_members_display_names()),
                inline=False,
            )

            # dm the backup if they are needed
            if missing > 0:
                for user in self.backup:
                    await user.send(embed=embed)

        # dm the users
        for user in self.joined:
            try:
                await user.send(embed=embed)
            except discord.Forbidden:
                pass

        # edit the channel message
        await self.message.edit(embed=embed, components=[])
        await self.__dump_to_db()

        # wait timedelta + 10 min
        await asyncio.sleep(time_to_start.seconds + 60 * 10)

        # delete the post
        await self.delete()

    async def send(self, ctx: ComponentContext = None):
        """send / edit the message in the channel"""

        embed = self.__return_embed()

        if not self.message:
            self.message = await self.channel.send(embed=embed, components=self.__buttons)
            self.creation_time = get_now_with_tz()
            first_send = True
        else:
            # acknowledge the button press
            if ctx:
                await ctx.edit_origin(embed=embed, components=self.__buttons)
            else:
                # todo check if has admin role @elevator site

                await self.message.edit(embed=embed, components=self.__buttons)
            first_send = False

        # update the database entry
        await self.__dump_to_db()

        # schedule the event
        await self.__schedule_event()

        # if message was freshly send, sort messages
        if first_send:
            await self.__sort_lfg_messages()

    async def delete(self, delete_command_user: discord.Member = None):
        """removes the message and also the database entries"""

        # todo check if delete_command_user has admin role @elevator site


        if not delete_command_user:
            delete_command_user = self.author

        # delete message
        if self.message:
            await self.message.delete()

        # try to delete voice channel, if that is currently empty
        if self.voice_channel and not self.voice_channel.members:
            try:
                await self.voice_channel.delete()
            except discord.NotFound:
                pass

        # delete DB entry
        result = await self.backend.delete(discord_member=delete_command_user, lfg_id=self.id)

        if result:
            # delete scheduler event
            # try to delete old job
            try:
                self.scheduler.remove_job(str(self.id))
            except JobLookupError:
                pass

    async def __sort_lfg_messages(self):
        """sort all the lfg messages in the guild by start_time"""

        # get all lfg ids
        results = await self.backend.get_all()
        if results:
            events = results.result["events"]

            # only continue if there is more than one event
            if len(events) <= 1:
                return

            # get three lists:
            # a list with the current message objs (sorted by asc creation date)
            # a list with the creation_time
            # and a list with the LfgMessage objs
            sorted_messages_by_creation_time = []
            sorted_creation_times_by_creation_time = []
            lfg_messages = []
            for event in events:
                sorted_messages_by_creation_time.append(await self.channel.fetch_message(event["message_id"]))
                sorted_creation_times_by_creation_time.append(event["creation_time"])
                lfg_messages.append(LfgMessage(
                    backend=self.backend,
                    client=self.client,
                    id=event["id"],
                    guild=self.guild,
                    channel=self.channel,
                    author=self.guild.get_member(event["author_id"]),
                    activity=event["activity"],
                    description=event["description"],
                    start_time=event["start_time"],
                    max_joined_members=event["max_joined_members"],
                    message=await self.channel.fetch_message(event["message_id"]),
                    creation_time=event["creation_time"],
                    joined=[self.guild.get_member(member_id) for member_id in event["joined_members"]],
                    backup=[self.guild.get_member(member_id) for member_id in event["alternate_members"]],
                    voice_channel=self.guild.get_channel(event["voice_channel_id"]),
                    voice_category_channel=self.guild.get_channel(event["voice_category_channel_id"])
                ))

            # sort the LfgMessages by their start_time
            sorted_lfg_messages = sorted(lfg_messages, reverse=True)

            # update the messages with their new message obj
            for message, creation_time, lfg_message in zip(
                sorted_messages_by_creation_time,
                sorted_creation_times_by_creation_time,
                sorted_lfg_messages,
            ):
                lfg_message.message = message
                lfg_message.creation_time = creation_time
                await lfg_message.send()

    def __get_joined_members_display_names(self) -> list[str]:
        """gets the display name of the joined members"""

        return [member.mention for member in self.joined]

    def __get_alternate_members_display_names(self) -> list[str]:
        """gets the display name of the alternate members"""

        return [member.mention for member in self.backup]


    def __return_embed(self) -> discord.Embed:
        """return the formatted embed"""

        embed = embed_message(
            footer=f"Creator: {self.author.display_name}   |   Your Time",
        )

        # add the fields with the data
        embed.add_field(
            name="Activity",
            value=self.activity,
            inline=True,
        )
        embed.add_field(
            name="Start Time",
            value=f"<t:{int(self.start_time.timestamp())}:f>",
            inline=True,
        )
        embed.add_field(
            name="ID",
            value=str(self.id),
            inline=True,
        )
        embed.add_field(
            name="Description",
            value=self.description,
            inline=False,
        )
        embed.add_field(
            name=f"Guardians Joined ({len(self.joined)}/{self.max_joined_members})",
            value=", ".join(self.__get_joined_members_display_names()) if self.joined else "_Empty Space :(_",
            inline=True,
        )
        if self.backup:
            embed.add_field(
                name="Backup",
                value=", ".join(self.__get_alternate_members_display_names()),
                inline=True,
            )

        # add the start time to the footer
        embed.timestamp = self.start_time

        return embed

    async def __dump_to_db(self):
        """updates the database entry"""

        await self.backend.update(
            lfg_id=self.id,
            discord_member=self.author,
            lfg_data=LfgUpdateData(
                channel_id=self.channel.id,
                message_id=self.message.id,
                voice_channel_id=self.voice_channel.id if self.voice_channel else None,
                activity=self.activity,
                description=self.description,
                start_time=self.start_time,
                max_joined_members=self.max_joined_members,
                joined_members=[member.id for member in self.joined],
                alternate_members=[member.id for member in self.backup],
            )
        )


    async def __schedule_event(self):
        """(re-) scheduled the event with apscheduler using the lfg_id as event_id"""

        # try to delete old job
        try:
            self.scheduler.remove_job(str(self.id))
        except JobLookupError:
            pass

        # using the id the job gets added
        timedelta = datetime.timedelta(minutes=10)
        run_date = self.start_time - timedelta
        now = get_now_with_tz()
        if run_date < now:
            run_date = now
        self.scheduler.add_job(
            notify_about_lfg_event_start,
            "date",
            (self.client, self.guild, self.id, timedelta),
            run_date=run_date,
            id=str(self.id),
        )

    async def __edit_start_time_and_send(self, start_time: datetime.datetime):
        """edit start time and sort messages again"""
        self.start_time = start_time

        # send
        await self.send()

        # sort again
        await self.__sort_lfg_messages()



async def notify_about_lfg_event_start(
    client: discord.Client,
    guild: discord.Guild,
    lfg_id: int,
    time_to_start: datetime.timedelta,
):
    """DMs the given list of users that the event is about to start"""

    lfg_message = await LfgMessage.from_lfg_id(
        lfg_id=lfg_id,
        client=client,
        guild=guild
    )
    await lfg_message.notify_about_start(time_to_start)
