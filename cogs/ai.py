import discord
from discord.ext import commands
import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.types import (
    HarmCategory,
    HarmBlockThreshold
)

import os
import json
import asyncio
import traceback
from collections import defaultdict

# ---------------- LOAD ENV ---------------- #

load_dotenv()

TOKEN = os.getenv("TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ---------------- CREATE DATA FOLDER ---------------- #

os.makedirs("data", exist_ok=True)

# ---------------- GEMINI SETUP ---------------- #

genai.configure(
    api_key=GEMINI_API_KEY
)

model = genai.GenerativeModel(
    "gemini-1.5-flash-latest"
)

# ---------------- DISCORD SETUP ---------------- #

AI_CHANNEL_ID = 1503661167984513025

MEMORY_FILE = "data/memory.json"



# ---------------- AI COG ---------------- #

class AI(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = defaultdict(float)
        self.memory = self.load_memory()

    # ---------------- LOAD MEMORY ---------------- #

    def load_memory(self):

        if not os.path.exists(MEMORY_FILE):
            return {}

        try:

            with open(MEMORY_FILE, "r") as f:
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

        # Ignore bots
        if message.author.bot:
            return

        # Only AI channel
        if message.channel.id != AI_CHANNEL_ID:
            return

        # Ignore commands
        if message.content.startswith("!"):
            return

        # ---------------- COOLDOWN ---------------- #

        current = asyncio.get_running_loop().time()

        if current - self.cooldowns[message.author.id] < 5:

            warning = await message.reply(
                "Slow down bro 😭"
            )

            await warning.delete(delay=3)
            return

        self.cooldowns[message.author.id] = current

        # ---------------- USER MEMORY ---------------- #

        user_id = str(message.author.id)

        if user_id not in self.memory:
            self.memory[user_id] = []

        # Save user message
        self.memory[user_id].append(
            {
                "role": "user",
                "content": message.content
            }
        )

        # Keep last 10 messages
        self.memory[user_id] = self.memory[user_id][-10:]

        # ---------------- BUILD CHAT HISTORY ---------------- #

        conversation = ""

        for msg in self.memory[user_id]:

            if msg["role"] == "user":

                conversation += (
                    f"User: {msg['content']}\n"
                )

            else:

                conversation += (
                    f"Bot: {msg['content']}\n"
                )

        # ---------------- PROMPT ---------------- #

        prompt = f"""
You are Sakura, a cute funny Discord anime girl AI.

Rules:
- Keep replies short
- Be playful
- Be natural
- Use emojis sometimes
- Avoid essays
- Talk like a real Discord friend

Conversation:
{conversation}

Reply naturally to the latest message.
"""

        # ---------------- GENERATE RESPONSE ---------------- #

        async with message.channel.typing():

            try:

                response = model.generate_content(
                    prompt,

                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH:
                        HarmBlockThreshold.BLOCK_NONE,

                        HarmCategory.HARM_CATEGORY_HARASSMENT:
                        HarmBlockThreshold.BLOCK_NONE,

                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT:
                        HarmBlockThreshold.BLOCK_NONE,

                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT:
                        HarmBlockThreshold.BLOCK_NONE,
                    }
                )

                # Empty response protection
                if not hasattr(response, "text"):

                    await message.reply(
                        "My brain stopped working 💀"
                    )

                    return

                reply = response.text[:2000]

                # Save bot reply
                self.memory[user_id].append(
                    {
                        "role": "assistant",
                        "content": reply
                    }
                )

                # Save memory
                self.save_memory()

                # Send reply
                await message.reply(reply)

            except Exception:

                traceback.print_exc()

                await message.reply(
                    "Gemini lost brain cells 💀"
                )

async def setup(bot):
    await bot.add_cog(ai(bot))


