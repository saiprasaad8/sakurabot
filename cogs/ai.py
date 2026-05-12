import discord
from discord.ext import commands
import google.generativeai as genai
from dotenv import load_dotenv

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
    "modela/gemini-1.5-flash-001"
)

# ---------------- CONFIG ---------------- #

AI_CHANNEL_ID = 1503661167984513025

MEMORY_FILE = "data/memory.json"

# ---------------- BOT ---------------- #

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

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

        # Only specific AI channel
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

        # ---------------- MEMORY ---------------- #

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

        # Keep only last 10 messages
        self.memory[user_id] = self.memory[user_id][-10:]

        # ---------------- BUILD CONVERSATION ---------------- #

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

        # ---------------- AI GENERATION ---------------- #

        async with message.channel.typing():

            try:

                response = await asyncio.to_thread(
                    model.generate_content,
                    prompt
                )

                print(response)

                reply = ""

                if response.candidates:

                    candidate = response.candidates[0]

                    if candidate.content.parts:

                        reply = (
                            candidate
                            .content
                            .parts[0]
                            .text
                        )

                # Empty reply protection
                if not reply:

                    await message.reply(
                        "Gemini replied with nothing 💀"
                    )

                    return

                # Discord limit
                reply = reply[:2000]

                # Save bot reply
                self.memory[user_id].append(
                    {
                        "role": "assistant",
                        "content": reply
                    }
                )

                # Save memory
                self.save_memory()

                # Send message
                await message.reply(reply)

            except Exception as e:

                traceback.print_exc()

                await message.reply(
                    f"Error: {str(e)}"
                )

# ---------------- READY EVENT ---------------- #

@bot.event
async def on_ready():

    print(f"{bot.user} is online!")

    try:

        response = await asyncio.to_thread(
            model.generate_content,
            "Say hello briefly"
        )

        print(response)

    except Exception:

        traceback.print_exc()



async def setup(bot):
    await bot.add_cog(AI(bot))

# ---------------- MAIN ---------------- #



# ---------------- START ---------------- #

