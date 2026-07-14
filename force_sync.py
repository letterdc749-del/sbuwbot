import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1517435995975585862

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.tree.command(name="test", description="test")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("works")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    # Force global sync first
    synced = await bot.tree.sync()
    print(f"Global: {len(synced)} commands")
    await bot.close()

bot.run(TOKEN)
