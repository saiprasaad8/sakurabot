import discord
from discord.ext import commands
from datetime import timedelta
import time

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # Spam tracking
        self.user_messages = {}

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        if not isinstance(message.author, discord.Member):
            return

        # Ignore admins/mods
        if message.author.guild_permissions.manage_messages:
            return

        # ---------------- ANTI EVERYONE / HERE ---------------- #

        if "@everyone" in message.content or "@here" in message.content:

            try:
                await message.delete()

                await message.author.timeout(
                    timedelta(minutes=30),
                    reason="Mass mention abuse"
                )

                warning = await message.channel.send(
                    f"⚠️ {message.author.mention} got timed out for mass mentioning."
                )

                await warning.delete(delay=5)

            except Exception as e:
                print(e)

            return

        # ---------------- CROSS CHANNEL SPAM ---------------- #

        now = time.time()

        if message.author.id not in self.user_messages:
            self.user_messages[message.author.id] = []

        self.user_messages[message.author.id].append(
            {
                "content": message.content,
                "channel": message.channel.id,
                "time": now
            }
        )

        # Keep only recent messages
        self.user_messages[message.author.id] = [
            msg for msg in self.user_messages[message.author.id]
            if now - msg["time"] <= 15
        ]

        recent = self.user_messages[message.author.id]

        # Detect same message across channels
        same_msgs = [
            msg for msg in recent
            if msg["content"] == message.content
        ]

        channels = set(msg["channel"] for msg in same_msgs)

        if len(channels) >= 3:

            try:
                await message.author.timeout(
                    timedelta(minutes=30),
                    reason="Cross-channel spam"
                )

                warning = await message.channel.send(
                    f"🚫 {message.author.mention} got timed out for spam."
                )

                await warning.delete(delay=5)

                # Reset user history
                self.user_messages[message.author.id] = []

            except Exception as e:
                print(e)

async def setup(bot):
    await bot.add_cog(Moderation(bot))