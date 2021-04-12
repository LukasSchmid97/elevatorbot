#
# import json
# import logging
# import os
# import pickle
#
# from functions.dataLoading import getPGCR, getStats, getProfile, returnManifestInfo
# from functions.database import getAllDestinyIDs, lookupDiscordID
# from functions.network import getJSONfromURL
# from static.dict import speedrunActivities, metricRaidCompletion, metricAvailableRaidCompletion, \
#     metricWinStreakWeeklyAllocation, metricRaidAllocation
#
#
# # return winner of the last game in the pvp history, if just those two players where in it
# async def returnCustomGameWinner(destinyID1, charIDs1, membershipType1, destinyID2):
#     for char in charIDs1:
#         staturl = f"https://www.bungie.net/Platform/Destiny2/{membershipType1}/Account/{destinyID1}/Character/{char}/Stats/Activities/?mode=0&count=1&page=0"
#         rep = await getJSONfromURL(staturl)
#         if rep and rep['Response']:
#             rep = json.loads(json.dumps(rep))
#             # if it's not a private game
#             if not rep["Response"]["activities"][0]["activityDetails"]["isPrivate"]:
#                 return None
#
#             # if it's not completed
#             if not int(rep["Response"]["activities"][0]["values"]["completed"]["basic"]["value"]) == 1:
#                 return None
#
#             ID = rep["Response"]["activities"][0]["activityDetails"]["instanceId"]
#             staturl = f"https://stats.bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/{ID}/"
#             rep2 = await getJSONfromURL(staturl)
#             if rep2 and rep2['Response']:
#                 rep2 = json.loads(json.dumps(rep2))
#
#                 # if more / less than 2 players
#                 if len(rep2["Response"]["entries"]) != 2:
#                     return None
#
#                 found1, found2 = False, False
#                 for player in rep2["Response"]["entries"]:
#                     if int(player["player"]["destinyUserInfo"]["membershipId"]) == int(destinyID1):
#                         found1 = True
#                     elif int(player["player"]["destinyUserInfo"]["membershipId"]) == int(destinyID2):
#                         found2 = True
#
#                 # players need to be the once specified
#                 if found1 and found2:
#                     if rep["Response"]["activities"][0]["values"]["standing"]["basic"]["displayValue"] == "Victory":
#                         return destinyID1
#                     else:
#                         return destinyID2
#     return None
#
#
# async def threadingBounties(activity, bounties, destinyID, discordID, experience_level_pve, experience_level_pvp, experience_level_raids):
#     # loop through all the bounties
#     for topic in bounties:
#         for experience in bounties[topic]:
#             # only go further if experience levels match
#             if topic == "Raids":
#                 if not ((experience_level_raids == 0 and experience == "New Players") or (
#                         experience_level_raids == 1 and experience == "Experienced Players")):
#                     continue
#             elif topic == "PvE":
#                 if not ((experience_level_pve == 0 and experience == "New Players") or (
#                         experience_level_pve == 1 and experience == "Experienced Players")):
#                     continue
#             elif topic == "PvP":
#                 if not ((experience_level_pvp == 0 and experience == "New Players") or (
#                         experience_level_pvp == 1 and experience == "Experienced Players")):
#                     continue
#
#             for bounty in bounties[topic][experience]:
#
#                 # check if user has done bounty this week already
#                 if playerHasDoneBounty(discordID, bounty):
#                     break
#
#                 requirements = bounties[topic][experience][bounty]
#
#                 # if true, a bounty is done
#                 done, index_multiple_points = await fulfillRequirements(requirements, activity, destinyID)
#                 if done:
#                     playerHasDoneBounty(discordID, bounty, done=True)
#                     addPoints(discordID, requirements, bounty, f"points_bounties_{topic.lower()}", index_multiple_points=index_multiple_points, clanmate_bonus=await checkIfDiscordmateInActivity(destinyID, activity["activityDetails"]["instanceId"]))
#                     print(f"""DiscordID {discordID} has completed bounty {bounty} with instanceID {activity["activityDetails"]["instanceId"]}""")
#
#
# async def threadingCompetitionBounties(activity, bounties, destinyID, discordID, leaderboard, sort_by):
#     # loop though all the competition bounties
#     for topic in bounties:
#         best_score = 0
#
#         for bounty, req in bounties[topic].items():  # there is only one item in here
#             # add to high score if new high score, otherwise skip
#             ret, sort_by_highest = await returnScore(req, activity, destinyID)
#
#             # next, if 0 got returned
#             if ret == 0:
#                 continue
#
#             # overwrite value if better
#             if sort_by_highest:
#                 if ret > best_score:
#                     best_score = ret
#             else:
#                 if (ret < best_score) or (best_score == 0):
#                     best_score = ret
#
#             # update leaderboards
#             leaderboard[topic].update({discordID: best_score})
#             sort_by.update({topic: sort_by_highest})
#
#     return leaderboard, sort_by
#
#
# # return true if name is in the pickle, otherwise false and add name to pickle
# def playerHasDoneBounty(discordID, name, done=False):
#     if not os.path.exists('functions/bounties/playerBountyStatus.pickle'):
#         file = {}
#     else:
#         with open('functions/bounties/playerBountyStatus.pickle', "rb") as f:
#             file = pickle.load(f)
#
#     # read
#     if not done:
#         try:
#             if name in file[discordID]:
#                 return True
#         except KeyError:
#             pass
#
#
#     # write
#     else:
#         try:
#             file[discordID].append(name)
#         except KeyError:
#             file[discordID] = [name]
#
#         with open('functions/bounties/playerBountyStatus.pickle', "wb") as f:
#             pickle.dump(file, f)
#
#     return False
#
#
# # adds points to the user
# def addPoints(discordID, requirements, name, leaderboard, index_multiple_points=None, clanmate_bonus=False):
#     points = requirements["points"]
#     if clanmate_bonus:
#         points *= 1.1
#         points = int(round(points, 0))
#
#     # if there are multiple possible points
#     if index_multiple_points is not None:
#         # add the lowman points
#         if "lowman" in requirements:
#             points = requirements["points"][index_multiple_points]
#
#     addLevel(points, leaderboard, discordID)
#
#     # log that action
#     logger = logging.getLogger('bounties')
#     logger.info(f"DiscordID '{discordID}' completed '{name}' and was credited '{points}' points in the leaderboard '{leaderboard}'.")
#
#
# # return true if another clanmate was in the activity
# async def checkIfDiscordmateInActivity(destinyID, activity_id):
#     discord_members = await getAllDestinyIDs()
#
#     pgcr = await getPGCR(activity_id)
#     for player in pgcr["Response"]["entries"]:
#         other_destinyID = int(player["player"]["destinyUserInfo"]["membershipId"])
#         if other_destinyID != destinyID and other_destinyID in discord_members:
#             return True
#
#     return False
#
#
# # saves the current competition bounties leaderboards. gets reset in awardCompetitionBountiesPoints()
# def changeCompetitionBountiesLeaderboards(leaderboard_name, leaderboard_data, sort_by_highest=True):  # leaderboard_date = {discordID: score}
#     if not os.path.exists('functions/bounties/competitionBountiesLeaderboards.pickle'):
#         file = {}
#     else:
#         with open('functions/bounties/competitionBountiesLeaderboards.pickle', "rb") as f:
#             file = pickle.load(f)
#
#     # create entry or get it if exists
#     if leaderboard_name not in file.keys():
#         file[leaderboard_name] = {}
#
#     # update the players score and sort it again
#     for key, value in leaderboard_data.items():
#         if key in file[leaderboard_name]:
#             if sort_by_highest:
#                 if file[leaderboard_name][key] > value:
#                     continue
#             else:
#                 if file[leaderboard_name][key] < value:
#                     continue
#         file[leaderboard_name][key] = value
#
#     file[leaderboard_name] = {k: v for k, v in sorted(file[leaderboard_name].items(), key=lambda item: item[1], reverse=sort_by_highest)}
#
#     # overwrite the file
#     with open('functions/bounties/competitionBountiesLeaderboards.pickle', "wb") as f:
#         pickle.dump(file, f)
#
#
# # gets the current competition bounties leaderboards. gets reset (file gets deleted) in awardCompetitionBountiesPoints()
# # leaderboards = {topic(fe. "Raids"): {id1: score, id2:score,...}, topic2: {...
# def getCompetitionBountiesLeaderboards():
#     # skip this is the file doesn't exist
#     if not os.path.exists('functions/bounties/competitionBountiesLeaderboards.pickle'):
#         return {}
#
#     # load the file
#     with open('functions/bounties/competitionBountiesLeaderboards.pickle', "rb") as f:
#         return pickle.load(f)
#
#
# # sets the exp level for "pve" - currently kd above 1.11
# async def experiencePvp(destinyID):
#     limit = 1.11    # since that includes hali :)
#
#     ret = await getStats(destinyID)
#     if ret:
#         kd = ret["mergedAllCharacters"]["results"]["allPvP"]["allTime"]["killsDeathsRatio"]["basic"]["value"]
#
#         exp = 1 if kd >= limit else 0
#         setLevel(exp, "exp_pvp", lookupDiscordID(destinyID))
#
#         return True
#     return False
#
#
# # sets the exp level for "pve" - currently time played above 500h
# async def experiencePve(destinyID):
#     limit = 500     # hours
#
#     ret = await getStats(destinyID)
#     if ret:
#         time_played = ret["mergedAllCharacters"]["results"]["allPvE"]["allTime"]["secondsPlayed"]["basic"]["value"]
#
#         exp = 1 if time_played >= (limit * 60 * 60) else 0
#         setLevel(exp, "exp_pve", lookupDiscordID(destinyID))
#
#         return True
#     return False
#
#
# # sets the exp level for "raids" - currently 35 raids and every raid cleared
# async def experienceRaids(destinyID):
#     limit_raids = 35            # total raids
#     limit_doneEach = 1          # does every raid need to be cleared
#
#     ret = await getProfile(destinyID, 1100)
#     if ret:
#         # check total raid completions
#         completions = 0
#         for raid in metricRaidCompletion:
#             completions += ret["metrics"]["data"]["metrics"][str(raid)]["objectiveProgress"]["progress"]
#
#         # check if every raid got cleared. Only looks at currently available raids
#         clears = True
#         for raid in metricAvailableRaidCompletion:
#             if limit_doneEach > ret["metrics"]["data"]["metrics"][str(raid)]["objectiveProgress"]["progress"]:
#                 clears = False
#                 break
#
#         exp = 1 if (completions >= limit_raids) and clears else 0
#         setLevel(exp, "exp_raids", lookupDiscordID(destinyID))
#
#         return True
#     return False
#
#
# # returns the sorted leaderboard for the specific topic. Returns dict = {id: score, ...}
# def returnLeaderboard(topic):
#     leaderboard = {}
#
#     # loop through users and get their individual score
#     for discordID in getBountyUserList():
#         level = getLevel(topic, discordID)
#         leaderboard.update({discordID: 0 if level is None else level})
#
#     # return sorted
#     return {k: v for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)}
#
#
# def saveAsGlobalVar(name, value, guild_id = None):
#     if not os.path.exists('functions/bounties/channelIDs.pickle'):
#         file = {}
#     else:
#         with open('functions/bounties/channelIDs.pickle', "rb") as f:
#             file = pickle.load(f)
#
#     if guild_id:
#         file["guild_id"] = guild_id
#     file[name] = value
#
#     with open('functions/bounties/channelIDs.pickle', "wb") as f:
#         pickle.dump(file, f)
#
#
# def deleteFromGlobalVar(name):
#     if os.path.exists('functions/bounties/channelIDs.pickle'):
#         with open('functions/bounties/channelIDs.pickle', "rb") as f:
#             file = pickle.load(f)
#
#         try:
#             file.pop(name)
#         except:
#             pass
#
#         with open('functions/bounties/channelIDs.pickle', "wb") as f:
#             pickle.dump(file, f)
#
#
# def getGlobalVar():
#     with open('functions/bounties/channelIDs.pickle', "rb") as f:
#         file = pickle.load(f)
#         return file
#
#
# # formats and sorts the entries. Input is dict = {id: score, id2: score2,...} output is list = [fancy sentence for id1, ...]
# async def formatLeaderboardMessage(client, leaderboard, user_id=None, limit=10):
#     # limit = how long the leaderboard will be
#
#     # sort that shit
#     leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)}
#
#     # format that shit
#     ranking = []
#     found = True if user_id is None else False
#     i = 1
#     for id, points in leaderboard.items():
#         if i > limit and found:
#             break
#
#         elif i > limit and not found:
#             # adding only this user
#             if id == user_id:
#                 ranking.append("...")
#                 ranking.append(str(i) + ") **" + client.get_user(id).display_name + "** _(Points: " + str(points) + ")_")
#                 break
#
#         else:
#             # if user id is given, do some fancy formating
#             user_name = (await client.fetch_user(id)).name
#             if id == user_id:
#                 found = True
#                 ranking.append(str(i) + ") **[ " + user_name + " ]** _(Points: " + str(points) + ")_")
#             else:
#                 ranking.append(str(i) + ") **" + user_name + "** _(Points: " + str(points) + ")_")
#
#         i += 1
#
#     return ranking
#
#
# # --------------------------------------------------------------
# # checking bounties requirements
# async def fulfillRequirements(requirements, activity, destinyID):
#     # write the requirement into the this list if it is done. At the end it will get check and if all the requirements are in there, true gets returned
#     complete_list = []
#
#     # needed for stuff like lowmans, where there are different points if you do better
#     index_multiple_points = None
#
#     hashID = activity["activityDetails"]["directorActivityHash"]
#     instance = activity["activityDetails"]["instanceId"]
#
#     if not (pgcr := await getPGCR(instance)):
#         return False, None
#
#     # clean runs
#     clean = cleanRuns(requirements, pgcr, destinyID)
#     if not clean:
#         return False, None
#
#
#     # loop through other requirements
#     for req in requirements["requirements"]:
#         # > tested <
#         if req == "allowedTypes":
#             ret = await returnManifestInfo("DestinyActivityDefinition", hashID)
#             if ret["Response"]["activityTypeHash"] in requirements["allowedTypes"]:
#                 complete_list.append(req)
#             else:
#                 return False, None
#
#
#         # > tested <
#         if req == "allowedActivities":
#             found = False
#             for activity_list in requirements["allowedActivities"]:
#                 if hashID in activity_list:
#                     complete_list.append(req)
#                     found = True
#                     break
#
#             if not found:
#                 return False, None
#
#
#         # > tested <
#         if req == "firstClear":
#             # get raid metrics for future comparison
#             individual_raid_clears = await getProfile(destinyID, 1100)
#             if individual_raid_clears:
#                 # loop though allowedActivities
#                 for activity_list in requirements["firstClear"]:
#                     for activity in activity_list:
#                         # make sure an allowed activity is selected
#                         if activity == hashID:
#                             # loop though tuples in metricRaidAllocation to find the correct metric hash
#                             for activities in metricRaidAllocation.keys():
#                                 if hashID in activities:
#                                     # set return to true if raid wasn't cleared before. So compare to one, since raid is now cleared. This shouldn't be a problem, since this gets check every 30mins, but it could bug out if they the raid 2x within that time
#                                     if individual_raid_clears["metrics"]["data"]["metrics"][str(metricRaidAllocation[activities][0])]["objectiveProgress"]["progress"] == 0:
#                                         complete_list.append(req)
#                                         break
#                                     else:
#                                         return False, None
#
#
#         # > tested <
#         if req == "customLoadout":
#             for player in pgcr["Response"]["entries"]:
#                 if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
#
#                     # loop through weapons
#                     all_weapons_ok = True
#                     for weapon in player["extended"]["weapons"]:
#                         weapon_info = await returnManifestInfo("DestinyInventoryItemDefinition", weapon["referenceId"])
#                         weapon_info_slot = weapon_info["Response"]["equippingBlock"]["equipmentSlotTypeHash"]
#                         weapon_info_type_name = weapon_info["Response"]["itemTypeDisplayName"]
#
#                         # check if weapon is allowed in slot
#                         weapon_ok = False
#                         for slot, allowed_weapon_type in requirements["customLoadout"].items():
#                             if slot == weapon_info_slot and allowed_weapon_type == weapon_info_type_name:
#                                 weapon_ok = True
#                         if not weapon_ok:
#                             all_weapons_ok = False
#
#                     # return true if all weapons were ok
#                     if all_weapons_ok:
#                         complete_list.append(req)
#                     else:
#                         return False, None
#
#
#         # > tested <
#         if req == "contest":
#             for player in pgcr["Response"]["entries"]:
#                 if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
#                     # get light level
#                     light_player = player["player"]["lightLevel"]
#
#                     # get activity light level
#                     ret = await returnManifestInfo("DestinyActivityDefinition", hashID)
#                     light_activity = ret["Response"]["activityLightLevel"]
#
#                     if (light_player + requirements["contest"]) <= light_activity:
#                         complete_list.append(req)
#                     else:
#                         return False, None
#
#
#         # > tested <
#         if req == "speedrun":
#             for player in pgcr["Response"]["entries"]:
#                 if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
#                     time = player["values"]["activityDurationSeconds"]["basic"]["value"]
#
#                     # do a different calc if a speedrun time was given
#                     if "speedrun" in requirements:
#                         if requirements["speedrun"] >= time:
#                             complete_list.append(req)
#                         else:
#                             return False, None
#
#                     # otherwise use the speedrun times in the dict
#                     else:
#                         found = False
#                         for activities in speedrunActivities.keys():
#                             if hashID in activities:
#                                 if speedrunActivities[activities] >= time:
#                                     found = True
#                                     break
#
#                         if found:
#                             complete_list.append(req)
#                         else:
#                             return False, None
#
#
#         # > tested <
#         elif req == "lowman":
#             for player in pgcr["Response"]["entries"]:
#                 if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
#                     player_count = int(player["values"]["playerCount"]["basic"]["value"])
#                     if player_count in requirements["lowman"]:
#                         # return the # of players also
#                         complete_list.append(req)
#                         index_multiple_points = requirements["lowman"].index(player_count)
#
#
#         # > tested <
#         if req == "totalKills":
#             for player in pgcr["Response"]["entries"]:
#                 if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
#                     if player["values"]["kills"]["basic"]["value"] >= requirements["totalKills"]:
#                         complete_list.append(req)
#                     else:
#                         return False, None
#
#
#         # > tested <
#         if req == "totalDeaths":
#             for player in pgcr["Response"]["entries"]:
#                 if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
#                     if player["values"]["deaths"]["basic"]["value"] <= requirements["totalDeaths"]:
#                         complete_list.append(req)
#                     else:
#                         return False, None
#
#
#         # > tested <
#         if req == "kd":
#             for player in pgcr["Response"]["entries"]:
#                 if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
#                     if player["values"]["killsDeathsRatio"]["basic"]["value"] >= requirements["kd"]:
#                         complete_list.append(req)
#                     else:
#                         return False, None
#
#
#         # > tested <
#         if req == "win":
#             for player in pgcr["Response"]["entries"]:
#                 if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
#                     if player["values"]["standing"]["basic"]["displayValue"] == "Victory":
#                         complete_list.append(req)
#                     else:
#                         return False, None
#
#
#         # > tested <
#         if req == "winStreak":
#             metrics = await getProfile(destinyID, 1100)
#             # loop trough allocation and set look
#             for activityTypes in metricWinStreakWeeklyAllocation.keys():
#                 ret = await returnManifestInfo("DestinyActivityDefinition", hashID)
#                 if ret["Response"]["activityTypeHash"] in activityTypes:
#                     if metrics["metrics"]["data"]["metrics"][str(metricWinStreakWeeklyAllocation[activityTypes][0])]["objectiveProgress"]["progress"] >= requirements["winStreak"]:
#                         complete_list.append(req)
#                         break
#                     else:
#                         return False, None
#
#
#         # > tested <
#         if req == "NFscore":
#             for player in pgcr["Response"]["entries"]:
#                 if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
#                     if player["values"]["score"]["basic"]["value"] >= requirements["NFscore"]:
#                         complete_list.append(req)
#                     else:
#                         return False, None
#
#     # only return true if everything else passes
#     all_done = True
#     for req in requirements["requirements"]:
#         if req not in complete_list:
#             all_done = False
#     return all_done, index_multiple_points
#
#
# # checking competition bounties scores
# async def returnScore(requirements, activity, destinyID):
#     score = 0
#     sort_by_highest = True
#
#     hashID = activity["activityDetails"]["directorActivityHash"]
#     instance = activity["activityDetails"]["instanceId"]
#
#     pgcr = await getPGCR(instance)
#
#     # clean runs
#     clean = cleanRuns(requirements, pgcr, destinyID)
#     if not clean:
#         return 0, sort_by_highest
#
#
#     # loop through other requirements
#     for req in requirements["requirements"]:
#         # > tested <
#         if req == "allowedTypes":
#             ret = await returnManifestInfo("DestinyActivityDefinition", hashID)
#             if ret["Response"]["activityTypeHash"] not in requirements["allowedTypes"]:
#                 return 0, sort_by_highest
#
#
#         # > tested <
#         elif req == "allowedActivities":
#             if hashID not in requirements["allowedActivities"]:
#                 return 0, sort_by_highest
#
#
#         # > tested <
#         elif req == "speedrun":
#             for player in pgcr["Response"]["entries"]:
#                 if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
#
#                     # set score
#                     sort_by_highest = False
#                     score = player["values"]["activityDurationSeconds"]["basic"]["value"] / 60
#                     score = round(score, 2)
#                     break
#
#
#         # > tested <
#         elif req == "lowman":
#             for player in pgcr["Response"]["entries"]:
#                 if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
#
#                     # set score
#                     sort_by_highest = False
#                     players = int(player["values"]["playerCount"]["basic"]["value"])
#                     if players <= 3:
#                         score = players
#
#
#         # todo: test, but should work
#         elif req == "noWeapons":
#             # return 0 if there are any weapon kills
#             for player in pgcr["Response"]["entries"]:
#                 try:
#                     for weapon in player["extended"]["weapons"]:
#                         if weapon["values"]["uniqueWeaponKills"] != 0:
#                             return 0, sort_by_highest
#                 except KeyError:
#                     print(f"Error at - {player['extended']}")
#
#
#         # > tested <
#         elif req == "totalKills":
#             for player in pgcr["Response"]["entries"]:
#                 if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
#
#                     # set score
#                     score = int(player["values"]["kills"]["basic"]["value"])
#                     break
#
#
#         # > tested <
#         elif req == "kd":
#             for player in pgcr["Response"]["entries"]:
#                 if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
#
#                     # set score
#                     score = player["values"]["killsDeathsRatio"]["basic"]["value"]
#                     score = round(score, 2)
#                     break
#
#
#         # > tested <
#         elif req == "NFscore":
#             for player in pgcr["Response"]["entries"]:
#                 if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
#
#                     # set score
#                     score = int(player["values"]["score"]["basic"]["value"])
#                     break
#
#         elif req == "flawless":
#             score = 1
#
#
#     # only return score if all other things have passed
#     return score, sort_by_highest
#
#
# # checks cp runs, if completed
# def cleanRuns(requirements, pgcr, destinyID):
#     # check if activity got completed
#     for player in pgcr["Response"]["entries"]:
#         if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
#             if player["values"]["completed"]["basic"]["value"] != 1:
#                 return False
#
#     # skip this if it's supposed to be a lowman
#     if "lowman" in requirements["requirements"]:
#         return True
#
#     # check for checkpoint runs
#     if pgcr["Response"]["startingPhaseIndex"] not in [-1, 0]:
#         return False
#
#     return True
#
#
#
#
#
#
#
#
#
#
