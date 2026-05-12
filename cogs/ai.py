import discord
from discord.ext import commands
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import asyncio
from collections import defaultdict

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-1.5-flash"
)

AI_CHANNEL_ID = 1503661167984513025

MEMORY_FILE = "data/memory.json"

class AI(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.cooldowns = defaultdict(float)

        self.memory = self.load_memory()

    # ---------------- LOAD MEMORY ---------------- #

    def load_memory(self):

        if not os.path.exists(MEMORY_FILE):
            return {}

        with open(MEMORY_FILE, "r") as f:

            try:
                return json.load(f)

            except:
                return {}

    # ---------------- SAVE MEMORY ---------------- #

    def save_memory(self):

        with open(MEMORY_FILE, "w") as f:
            json.dump(
                self.memory,
                f,
                indent=4
            )

    # ---------------- AI CHAT ---------------- #

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        if message.channel.id != AI_CHANNEL_ID:
            return

        if message.content.startswith("!"):
            return

        # ---------------- COOLDOWN ---------------- #

        current = asyncio.get_event_loop().time()

        if current - self.cooldowns[message.author.id] < 5:

            warning = await message.reply(
                "Slow down bro 😭"
            )

            await warning.delete(delay=3)
            return

        self.cooldowns[message.author.id] = current

        user_id = str(message.author.id)

        # Create user memory if not exists
        if user_id not in self.memory:
            self.memory[user_id] = []

        # Save user message
        self.memory[user_id].append(
            {
                "role": "user",
                "content": message.content
            }
        )

        # Keep only last 10 messages
        self.memory[user_id] = self.memory[user_id][-10:]

        # Build conversation
        conversation = ""

        for msg in self.memory[user_id]:

            if msg["role"] == "user":
                conversation += f"User: {msg['content']}\n"

            else:
                conversation += f"Bot: {msg['content']}\n"

        prompt = f"""
        You are a funny Discord AI bot.

        Keep replies short.
        Be playful and natural.
        Avoid essays.

        Conversation History:
        {conversation}

        Reply naturally to the latest message.
        """

        async with message.channel.typing():

            try:

                response = model.generate_content(prompt)

                reply = response.text[:2000]

                # Save bot reply
                self.memory[user_id].append(
                    {
                        "role": "assistant",
                        "content": reply
                    }
                )

                # Save to JSON
                self.save_memory()

                await message.reply(reply)

            except Exception as e:

                print(e)

                await message.reply(
                    "Gemini lost brain cells 💀"
                )

async def setup(bot):
    await bot.add_cog(AI(bot))