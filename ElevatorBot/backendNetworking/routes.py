import os


base_route = f"""http://{os.environ.get("BACKEND_HOST")}:{os.environ.get("BACKEND_PORT")}/"""
destiny_base_route = base_route + "destiny/{guild_id}/{discord_id}/"

# elevators discord guilds
elevator_servers_get = base_route + "elevator/discordServers/get/"
elevator_servers_add = base_route + "elevator/discordServers/add/{guild_id}/"
elevator_servers_delete = base_route + "elevator/discordServers/delete/{guild_id}/"

# profile
destiny_profile_from_discord_id_route = base_route + "profile/discord/{discord_id}/"
destiny_profile_from_destiny_id_route = base_route + "profile/destiny/{destiny_id}/"
destiny_profile_delete_route = base_route + "profile/delete/{discord_id}/"

# account
destiny_account_route = destiny_base_route + "account/"
destiny_account_name_route = destiny_account_route + "name/"  # GET
destiny_account_solos_route = destiny_account_route + "solos/"  # GET
destiny_account_characters_route = destiny_account_route + "characters/"  # GET
destiny_account_stat_route = destiny_account_route + "stat/{stat_category}/{stat_name}/"  # GET
destiny_account_stat_characters_route = destiny_account_route + "stat/characters/{stat_category}/{stat_name}/"  # GET

# lfg system
destiny_lfg_route = base_route + "destiny/{guild_id}/lfg/"
destiny_lfg_get_route = destiny_lfg_route + "get/{lfg_id}/"  # GET
destiny_lfg_get_all_route = destiny_lfg_route + "get/all/"  # GET
destiny_lfg_update_route = destiny_lfg_route + "{discord_id}/update/{lfg_id}/"  # POST
destiny_lfg_delete_route = destiny_lfg_route + "{discord_id}/delete/{lfg_id}/"  # DELETE
destiny_lfg_create_route = destiny_lfg_route + "{discord_id}/create/"  # POST

# clan
destiny_clan_route = destiny_base_route + "clan/"
destiny_clan_get_route = destiny_clan_route + "get/"
destiny_clan_get_members_route = destiny_clan_route + "get/members/"
destiny_clan_search_members_route = destiny_clan_route + "get/members/search/{search_phrase}/"
destiny_clan_invite_route = destiny_clan_route + "invite/"
destiny_clan_link_route = destiny_clan_route + "link/"
destiny_clan_unlink_route = destiny_clan_route + "unlink/"
