from keep_alive import keep_alive
import discord
from discord.ext import commands

keep_alive()  # inicia el mini servidor Flask

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

bot.run("TU_TOKEN_AQUI")
