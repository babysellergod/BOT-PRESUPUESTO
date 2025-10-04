from keep_alive import keep_alive
import discord
from discord.ext import commands
import asyncio

keep_alive()  # inicia el mini servidor Flask

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

# 🔹 Cargar el archivo presupuesto.py
async def load_commands():
    await bot.load_extension("presupuesto")

async def main():
    async with bot:
        await load_commands()
        await bot.start(os.getenv("DISCORD_TOKEN")) # cambia por tu token

asyncio.run(main())
