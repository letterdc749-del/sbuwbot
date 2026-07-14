import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1517435995975585862

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.tree.command(name="test", description="Test command")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("it works")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(f"Commands in tree: {[c.name for c in bot.tree.get_commands()]}")
    try:
        # Try global sync first
        synced = await bot.tree.sync()
        print(f"Global synced: {len(synced)} commands")
    except Exception as e:
        print(f"Global sync error: {e}")
    try:
        # Try guild sync
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"Guild synced: {len(synced)} commands")
    except Exception as e:
        print(f"Guild sync error: {e}")

bot.run(TOKEN)
