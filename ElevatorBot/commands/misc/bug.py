from concurrent.futures import ThreadPoolExecutor

from dis_snek import ActionRow, Button, ButtonStyles
from dis_snek.models import InteractionContext, OptionTypes, slash_command, slash_option
from github.GithubObject import NotSet

from ElevatorBot.backendNetworking.github import get_github_labels, get_github_repo
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.descendOnlyIds import descend_channels


class Bug(BaseScale):
    @slash_command(name="bug", description="Use this if you want to report any bugs to the developer")
    @slash_option(
        name="message",
        description="Please describe **in detail** the bug you have noticed",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    async def _bug(self, ctx: InteractionContext, message: str):
        components = None
        embed = embed_message("Bug Report", f"{message}\n⁣\n- by {ctx.author.mention}")

        # upload that to GitHub
        repo = get_github_repo()
        if repo:
            # run those in a thread because it is blocking
            with ThreadPoolExecutor() as pool:
                issue = await ctx.bot.loop.run_in_executor(
                    pool,
                    repo.create_issue,
                    f"Bug Report by Discord User `{ctx.author.username}#{ctx.author.discriminator}`",
                    message,
                    NotSet,
                    NotSet,
                    get_github_labels(),
                )

            components = [
                ActionRow(
                    Button(style=ButtonStyles.URL, label="View the Bug Report", url=issue.url),
                ),
                ActionRow(
                    Button(custom_id="github", style=ButtonStyles.GREEN, label="Delete Issue"),
                ),
            ]
            embed.set_footer(f"ID: {issue.id}")

        # send that in the bot dev channel
        await descend_channels.bot_dev_channel.send(embeds=embed, components=components)

        await ctx.send(
            ephemeral=True,
            embeds=embed_message(
                "Success",
                f"Your message has been forwarded to my developer\nDepending on the clarity of your bug report, you may or may not be contacted by them",
            ),
            components=components[:1],
        )


def setup(client):
    Bug(client)
