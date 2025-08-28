import os
import logging
import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks
from modules.auto_reply import qa
from modules.utils.sqlite_db import initialize_database
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix='/', intents=intents,
)

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

@bot.event
async def setup_hook():
  for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        await bot.load_extension(f'cogs.{filename[:-3]}')
        print(f"Loaded Cog: {filename[:-3]}")
    else:
        print("Unable to load pycache folder.")

@bot.event
async def on_ready():
    await bot.tree.sync()
    initialize_database()
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    answer = qa.find_best_match(message, threshold=0.7)
    if answer:
        await message.reply(answer)

# --- Run the Bot ---
if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)