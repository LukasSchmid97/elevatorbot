error_codes_and_responses = {
    "DestinyIdNotFound": "I don't possess information for the user with the DestinyID `{destiny_id}` \nPlease `/registration` to use my commands",
    "DiscordIdNotFound": "I don't possess information for {discord_member.mention} \nPlease `/registration` to use my commands",
    "CharacterIdNotFound": "{discord_member.mention} does not have a character with that ID",
    "NoToken": "{discord_member.mention} registration is outdated \nPlease `/registration` again",
    "BungieUnauthorized": "The request was not authorized correctly",
    "BungieDed": "The Bungie API is down at the moment \nPlease try again later",
    "BungieNoDestinyId": "You do not seem to have a Destiny 2 account",
    "BungieBadRequest": "I got a 404 error. This shouldn't happen, my bad. Consider me punished",
    "BungieDestinyItemNotFound": "{discord_member.mention} doesn't own this item",
    "BungieDestinyItemNotExist": "I tried to find an item that does not exist \nPlease excuse this mishap while I punish myself",
    "BungieDestinyPrivacyRestriction": "{discord_member.mention} has a private profile \nPlease change your [privacy settings](https://www.bungie.net/en/Profile/Settings/)",
    "BungieClanTargetDisallowsInvites": "{discord_member.mention} is not allowing clan invites \nPlease change your [privacy settings](https://www.bungie.net/en/Profile/Settings/)",
    "BungieGroupMembershipNotFound": "{discord_member.mention} is not in the clan and can thus not be removed \nI felt like adding them just to remove them was going too far",
    "UnknownError": "I got an unknown error while handling your request \nPlease contact a developer",
    "ProgrammingError": "The impossible happened... I was programmed incorrectly :( \nPlease contact a developer",
    "NoClanLink": "This guild does not have a linked clan\nPlease have an admin run `/setup clan link` to set this up",
    "NoClan": "The linked clan could not be found. Either bungie is having problems, or the clan link is broken\nPlease consider having an admin run `/setup clan link` again",
    "UserNoClan": "{discord_member.mention} is not in any clan",
    "ClanNoPermissions": "Could not invite {discord_member.mention} to the linked clan, since the user who linked the clan to this discord guild is no longer a Destiny 2 clan admin\nPlease have an Admin re-link the clan to fix this",
    "NoLfgEventWithIdForGuild": "No LFG event was found for that ID \nPlease try again",
    "NoLfgEventPermissions": "{discord_member.mention} does not have permissions to edit this LFG event \nOnly the creator and discord admins can do that",
    "RoleLookupTimedOut": "The role lookup for {discord_member.mention} timed out. This shouldn't happen, my bad. Consider me punished",
    "PollNoPermission": "{discord_member.mention} does not have permissions to modify this poll",
    "PollOptionNotExist": "This option does not exist. Make sure you spelled it correctly",
    "PollNotExist": "This poll ID does not exist",
    "NoActivityFound": "{discord_member.mention} has never done an activity that fulfills the given requirements",
    "WeaponUnused": "{discord_member.mention} has never used the specified weapon in any activity that fulfills the given requirements",
    "WeaponTypeMismatch": "This weapon does not belong to the specified weapon type",
    "WeaponDamageTypeMismatch": "This weapon does not have the specified damage type",
    "PersistentMessageNotExist": "This persistent message does not exist",
    "RoleNotExist": "This role is not achievable through me",
    "NoGiveaway": "This is not a giveaway I am hosting",
    "AlreadyInGiveaway": "I would never forget you, do not worry <3\nYou have already entered the giveaway",
}
