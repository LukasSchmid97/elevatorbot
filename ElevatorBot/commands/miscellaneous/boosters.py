from dis_snek.models import InteractionContext, Member, TimestampStyles, slash_command

from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message


class Boosters(BaseScale):
    @slash_command(name="boosters", description="Prints all premium subscribers (boosters) of this discord server")
    async def boosters(self, ctx: InteractionContext):

        sorted_premium_subscribers: list[Member] = sorted(
            ctx.guild.premium_subscribers, key=lambda m: m.premium_since, reverse=True
        )

        embed = embed_message(
            f"{ctx.guild.name} Nitro Boosters",
            ",\n".join(
                [
                    f"{member.mention} since {member.premium_since.format(TimestampStyles.ShortDateTime)}"
                    for member in sorted_premium_subscribers
                ]
            ),
        )

        await ctx.send(embeds=embed)


def setup(client):
    Boosters(client)
