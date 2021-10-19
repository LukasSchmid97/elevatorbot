import asyncio

from dis_snek.client import Snake
from dis_snek.models import listen
from dis_snek.models.enums import Intents

from ElevatorBot.discordEvents.base import register_discord_events
from ElevatorBot.misc.discordStatus import update_status
from ElevatorBot.misc.initBackgroundEvents import register_background_events
from ElevatorBot.misc.initDocs import create_command_docs
from ElevatorBot.misc.initLogging import init_logging
from ElevatorBot.misc.veryMisc import yield_files_in_folder
from ElevatorBot.static.emojis import custom_emojis
from ElevatorBot.webserver.server import run_webserver
from settings import DISCORD_BOT_TOKEN
from settings import SYNC_COMMANDS


first_start = True


if __name__ == "__main__":
    # config logging
    init_logging()

    # print ascii art
    print("----------------------------------------------------------------------------------------")
    print(
        """
          ______   _                          _                    ____            _
         |  ____| | |                        | |                  |  _ \          | |
         | |__    | |   ___  __   __   __ _  | |_    ___    _ __  | |_) |   ___   | |_
         |  __|   | |  / _ \ \ \ / /  / _` | | __|  / _ \  | '__| |  _ <   / _ \  | __|
         | |____  | | |  __/  \ V /  | (_| | | |_  | (_) | | |    | |_) | | (_) | | |_
         |______| |_|  \___|   \_/    \__,_|  \__|  \___/  |_|    |____/   \___/   \__|
        """
    )
    print("----------------------------------------------------------------------------------------\n")
    print("Starting Up...")

    # enable intents to allow certain events
    # see https://discord.com/developers/docs/topics/gateway#gateway-intents
    intents = Intents.new(
        guilds=True,
        guild_members=True,
        guild_messages=True,
        guild_voice_states=True,
    )

    # actually get the bot obj
    client = Snake(
        intents=intents,
        sync_interactions=SYNC_COMMANDS,
        delete_unused_application_cmds=True,
    )

    # add discord events and handlers
    register_discord_events(client)

    @listen()
    async def on_ready():
        """Get's triggered on startup and re-connects"""

        # only run this on first startup
        global first_start
        if not first_start:
            return
        first_start = False

        print("Loading Background Events...")
        await register_background_events(client)

        print("Creating docs for commands...")
        create_command_docs(client)

        print("Launching the Status Changer...")
        asyncio.create_task(update_status(client))

        print("Start Webserver...")
        asyncio.create_task(run_webserver(client=client))

        print("Load Custom Emoji...")
        await custom_emojis.init_emojis(client)

        print("Startup Finished!\n")
        print("--------------------------\n")

    i = 0

    # load commands
    print("Loading Commands...")
    for path in yield_files_in_folder("commands", "py"):
        # todo remove once all commands are ported
        try:
            client.load_extension(path)
        except:
            print(f"Couldn't load {path}")

    global_commands = len(client.interactions[0])
    print(f"< {global_commands} > Global Commands Loaded")

    local_commands = 0
    for key, value in client.interactions.items():
        if key != 0:
            local_commands += len(value)
    print(f"< {local_commands} > Local Commands Loaded")

    # load context menus
    print("Loading Context Menus...")
    for path in yield_files_in_folder("contextMenus", "py"):
        client.load_extension(path)

    global_context_menus = len(client.interactions[0])
    print(f"< {global_context_menus - global_commands} > Global Context Menus Loaded")

    local_context_menus = 0
    for key, value in client.interactions.items():
        if key != 0:
            local_context_menus += len(value)
    print(f"< {local_context_menus - local_commands} > Local Context Menus Loaded")

    # run the bot
    client.start(DISCORD_BOT_TOKEN)
