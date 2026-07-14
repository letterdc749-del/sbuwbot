import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1517435995975585862

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    commands = await bot.http.get_guild_commands(bot.application_id, GUILD_ID)
    print(f"Guild commands ({len(commands)}):")
    for cmd in commands:
        print(f"  - /{cmd['name']}")
    global_commands = await bot.http.get_global_commands(bot.application_id)
    print(f"Global commands ({len(global_commands)}):")
    for cmd in global_commands:
        print(f"  - /{cmd['name']}")
    await bot.close()

bot.run(TOKEN)
