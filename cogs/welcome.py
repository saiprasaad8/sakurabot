import discord
from discord.ext import commands

WELCOME_CHANNEL_ID = 1111194175845715998

BANNER_URL = ""

class Welcome(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):

        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)

        if not channel:
            return

        embed = discord.Embed(
            title="✨ Welcome ✨",
            description=(
                f"Welcome {member.mention} to "
                f"**{member.guild.name}** 🎉"
            ),
            color=discord.Color.blurple()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.set_image(url=BANNER_URL)

        embed.set_footer(
            text=f"Member #{member.guild.member_count}"
        )

        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))