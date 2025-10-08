from keep_alive import keep_alive
import discord
from discord.ext import commands
import asyncio
import os

keep_alive()  # Inicia el servidor Flask

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# 🔹 Cargar los archivos de comandos (Cogs)
async def load_commands():
    await bot.load_extension("presupuesto")
    await bot.load_extension("precio")

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    try:
        synced = await bot.tree.sync()  # sincroniza los comandos slash con Discord
        print(f"🌐 {len(synced)} comandos sincronizados (slash).")
    except Exception as e:
        print(f"⚠️ Error al sincronizar comandos: {e}")

async def main():
    async with bot:
        await load_commands()  # carga los comandos ANTES de iniciar el bot
        await bot.start(os.getenv("DISCORD_TOKEN"))  # token seguro desde Render

asyncio.run(main())
