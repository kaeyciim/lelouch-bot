import os
import discord
from discord.ext import commands

intents = discord.Intents.all()
Bot = commands.Bot(command_prefix="/", intents=intents)

@Bot.event
async def setup_hook():
    for filename in os.listdir("./Cogs"):
        if filename.endswith(".py"):
            await Bot.load_extension(f"Cogs.{filename[:-3]}")
    
    # Komutları global (genel) olarak senkronize eder
    await Bot.tree.sync()

@Bot.event
async def on_ready():
    print(f"{Bot.user} hazır ve Slash komutları senkronize edildi!")

Bot.run("MTU0NjkyNjQ2MzM4NTg2NjI5MQ.GnclAP.HfKhQxYtLi4hKccBtbbJr4g0z_87jrfQ9IpvbU")