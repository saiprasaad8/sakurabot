import discord
from discord.ext import commands

LOG_CHANNEL_ID = 1503659715241054239

class Logging(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):

        if message.author.bot:
            return

        channel = self.bot.get_channel(LOG_CHANNEL_ID)

        if not channel:
            return

        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=discord.Color.red()
        )

        embed.add_field(
            name="User",
            value=message.author.mention,
            inline=True
        )

        embed.add_field(
            name="Channel",
            value=message.channel.mention,
            inline=True
        )

        embed.add_field(
            name="Message",
            value=message.content or "No content",
            inline=False
        )

        embed.set_footer(
            text=f"User ID: {message.author.id}"
        )

        await channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):

        if before.author.bot:
            return

        if before.content == after.content:
            return

        channel = self.bot.get_channel(LOG_CHANNEL_ID)

        if not channel:
            return

        embed = discord.Embed(
            title="✏️ Message Edited",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="User",
            value=before.author.mention,
            inline=True
        )

        embed.add_field(
            name="Channel",
            value=before.channel.mention,
            inline=True
        )

        embed.add_field(
            name="Before",
            value=before.content[:1000] or "Empty",
            inline=False
        )

        embed.add_field(
            name="After",
            value=after.content[:1000] or "Empty",
            inline=False
        )

        await channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_member_join(self, member):

        channel = self.bot.get_channel(LOG_CHANNEL_ID)

        if not channel:
            return

        embed = discord.Embed(
            title="📥 Member Joined",
            description=f"{member.mention} joined the server.",
            color=discord.Color.green()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        await channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_member_remove(self, member):

        channel = self.bot.get_channel(LOG_CHANNEL_ID)

        if not channel:
            return

        embed = discord.Embed(
            title="📤 Member Left",
            description=f"{member} left the server.",
            color=discord.Color.red()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        await channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):

        channel = self.bot.get_channel(LOG_CHANNEL_ID)

        if not channel:
            return

        embed = discord.Embed(
            title="🔨 Member Banned",
            description=f"{user} was banned.",
            color=discord.Color.dark_red()
        )

        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Logging(bot))
