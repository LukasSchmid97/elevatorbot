import discord

from discord_slash import SlashContext

from functions.database import lookupDestinyID, lookupSystem
from functions.formating import embed_message
from functions.miscFunctions import has_elevated_permissions


async def get_user_obj(ctx: SlashContext, kwargs: dict = None):
    """ Returns the user object of the mentioned user in the kwargs, if emtpy, return author """

    if "user" in kwargs:
        return kwargs["user"]
    return ctx.author


async def get_user_obj_admin(ctx: SlashContext, kwargs: dict = None, allowed_users: list = None):
    """ Shadows get_user_obj(), but only returns if user has elevated permssions (admin / mod) or arg wasn't used or author is in the allowed_users list of int ids"""

    if allowed_users is None:
        allowed_users = []

    user = await get_user_obj(ctx, kwargs)

    if await has_elevated_permissions(ctx.author, ctx.guild, ctx) or user == ctx.author or ctx.author.id in allowed_users:
        return user
    return


async def get_destinyID_and_system(ctx: SlashContext, discord_user):
    """" takes either a discord user_id or the user obj and return user obj, destinyID and system or None """

    var_type = type(discord_user)

    if var_type == int:
        user = ctx.bot.get_user(discord_user)
    elif var_type == discord.user.User or var_type == discord.member.Member:
        user = discord_user
    else:
        return None, None, None

    destinyID = lookupDestinyID(user.id)
    system = lookupSystem(destinyID)

    if not (destinyID and system):
        await ctx.send(hidden=True, embed=embed_message(
            'Error',
            f'I possess no information about {user.display_name}. \nPlease `/registerdesc` first'
        ))
        return None, None, None

    return user, destinyID, system



