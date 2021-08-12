import datetime
from typing import Union, Optional

import discord

from database.database import get_persistent_message, insertPersistentMessage, \
    getallSteamJoinIDs, updatePersistentMessage, getAllPersistentMessages, deletePersistentMessage
from functions.formating import embed_message
from networking.bungieAuth import handle_and_return_token


async def get_persistent_message_or_channel(
    client: discord.Client,
    message_name: str,
    guild_id: int
) -> Optional[Union[discord.VoiceChannel, discord.TextChannel, discord.Message]]:
    """
    Gets the persistent message for the specified name and guild and channel. If it doesnt exist, it will return the channel and if that doesnt exit it will return False
    Returns message obj or None
    """

    res = await get_persistent_message(message_name, guild_id)

    # check if msg exist
    if not res:
        return None

    # otherwise return message. Return False should bot_status be asked for on other servers then descend
    channel: Union[discord.VoiceChannel, discord.TextChannel] = client.get_channel(res[0])
    if not channel:
        return None
    try:
        message: discord.Message = await channel.fetch_message(res[1])
        return message
    except (discord.NotFound, AttributeError):
        return channel


async def make_persistent_message(
    client,
    message_name,
    guild_id,
    channel_id,
    reaction_id_list=None,
    components: dict = None,
    message_text=None,
    message_embed=None,
    no_message=False
):
    """
    Creates a new persistent message entry in the DB or changes the old one
    Returns message obj
    """

    if reaction_id_list is None:
        reaction_id_list = []

    message = None
    if not no_message:
        assert (message_text or message_embed), "Need to input either text or embed"
        assert (not (message_text and message_embed)), "Need to input either text or embed, not both"

        # make new message
        channel = client.get_channel(channel_id)
        message = await channel.send(content=message_text, embed=message_embed, components=components)

        # react if wanted
        for emoji_id in reaction_id_list:
            emoji = client.get_emoji(emoji_id)
            await message.add_reaction(emoji)

    # save msg in DB
    # check if msg exists
    res = await get_persistent_message(message_name, guild_id)

    # update
    if res:
        # delete old msg
        channel = client.get_channel(res[0])
        try:
            old_message = await channel.fetch_message(res[1])
            await old_message.delete()
        except discord.errors.NotFound:
            pass

        await updatePersistentMessage(message_name, guild_id, channel_id, message.id if message else 0, reaction_id_list)

    # insert
    else:
        await insertPersistentMessage(message_name, guild_id, channel_id, message.id if message else 0, reaction_id_list)

    return message


async def delete_persistent_message(
    message,
    message_name,
    guild_id
):
    """ Delete the persistent message for the specified name and guild """

    await message.delete()
    await deletePersistentMessage(message_name, guild_id)


async def check_reaction_for_persistent_message(
    client,
    payload
):
    # get all persistent messages
    persistent_messages = await getAllPersistentMessages()

    # loop through the msgs and check if reaction was on in
    for persistent_message in persistent_messages:
        persistent_message_id = persistent_message[3]

        # if it was, handle it
        if payload.message_id == persistent_message_id:
            await handle_persistent_message_reaction(client, payload, persistent_message)


async def handle_persistent_message_reaction(
    client,
    payload,
    persistent_message
):
    message_name = persistent_message[0]
    guild_id = persistent_message[1]
    channel_id = persistent_message[2]
    message_id = persistent_message[3]
    reactions_id_list = persistent_message[4]

    channel = client.get_channel(channel_id)
    message = await channel.fetch_message(message_id)

    # check if the reactions are ok, else remove them. Only do that when set reactions exist tho
    if reactions_id_list and payload.emoji.id not in reactions_id_list:
        await message.remove_reaction(payload.emoji, payload.member)
        return

    # only allow registered users to participate
    elif message_name == "tournament":
        if not (await handle_and_return_token(payload.member.id)).token:
            await message.remove_reaction(payload.emoji, payload.member)
            await payload.member.send(
                embed=embed_message(
                    "Error",
                    "You need to register first before you can join a tournament. \nTo do that please use `/registerdesc` in <#670401854496309268>"
                )
            )


async def steamJoinCodeMessage(
    client,
    guild
):
    # get all IDs
    data = await getallSteamJoinIDs()

    # convert discordIDs to names
    clean_data = {}
    for entry in data:
        # get display_name. If that doesnt work user isnt in guild, thus ignore him
        try:
            clean_data[guild.get_member(entry[0]).display_name] = entry[1]
        except AttributeError:
            continue

    # sort and put in two lists
    sorted_data = {k: str(v) for k, v in sorted(
        clean_data.items(), key=lambda
            item: item[0], reverse=False
    )}

    # put in two lists for the embed
    name = list(sorted_data.keys())
    code = list(sorted_data.values())

    # create new message
    embed = embed_message(
        "Steam Join Codes",
        "Here you can find a updated list of Steam Join Codes. \nUse `/id set <id>` to set appear here and `/id get <user>` to find a code without looking here"
    )

    # add name field
    embed.add_field(name="User", value="\n".join(name), inline=True)

    # add code field
    embed.add_field(name="Code", value="\n".join(code), inline=True)

    # get msg object
    message = await get_persistent_message_or_channel(client, "steamJoinCodes", guild.id)

    # edit msg
    await message.edit(embed=embed)


async def bot_status(
    client: discord.Client,
    field_name: str,
    time: datetime.datetime
) -> None:
    """
    takes the field (name) and the timestamp of last update

    Current fields in use:
        "Database Update"
        "Manifest Update"
        "Token Refresh"
        "Member Role Update"
        "Achievement Role Update"
        "Bounties - Experience Update"
        "Bounties - Generation"
        "Bounties - Completion Update"
        "Steam Player Update"
        "Vendor Armor Roll Lookup"
    """

    # get msg. guild id is one, since there is only gonna be one msg
    message = await get_persistent_message_or_channel(client, "botStatus", 1)
    if not message:
        return

    embed = embed_message(
        "Status: Last valid..."
    )

    embeds = message.embeds[0]
    fields = embeds.fields

    found = False
    formated_time = f"""{time.strftime("%d/%m/%Y, %H:%M")} UTC"""
    for field in fields:
        embed.add_field(name=field.name, value=formated_time if field.name == field_name else field.value, inline=True)
        if field.name == field_name:
            found = True

    if not found:
        embed.add_field(name=field_name, value=formated_time, inline=True)

    await message.edit(embed=embed)
