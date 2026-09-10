import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import random

DATA_FILE = "levels.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        # Her mesajda veriyi güncel tutmak için baştan yükleyelim
        self.data = load_data()

        user_id = str(message.author.id)
        if user_id not in self.data:
            self.data[user_id] = {"xp": 0, "level": 1}

        self.data[user_id]["xp"] += random.randint(5, 15)
        current_xp = self.data[user_id]["xp"]
        current_level = self.data[user_id]["level"]
        next_level_xp = current_level * 100

        if current_xp >= next_level_xp:
            self.data[user_id]["level"] += 1
            new_level = self.data[user_id]["level"]
            
            embed = discord.Embed(
                title="Level Atlandı",
                description=f"{message.author.mention} seviye atladı ve Seviye {new_level} oldu.",
                color=discord.Color.blurple()
            )
            embed.set_thumbnail(url=message.author.display_avatar.url)
            await message.channel.send(embed=embed)

        save_data(self.data)

    @app_commands.command(name="seviye", description="Mevcut seviyeni ve XP durumunu gösterir.")
    async def seviye(self, interaction: discord.Interaction, üye: discord.Member = None):
        self.data = load_data() # Güncel veriyi dosyadan çek
        target = üye or interaction.user
        user_id = str(target.id)

        if user_id not in self.data:
            await interaction.response.send_message(f"{target.display_name} henüz hiç XP kazanmamış.", ephemeral=True)
            return

        user_xp = self.data[user_id]["xp"]
        user_level = self.data[user_id]["level"]
        needed_xp = user_level * 100

        embed = discord.Embed(title=f"{target.display_name} - Seviye Bilgisi", color=discord.Color.blurple())
        embed.add_field(name="Seviye", value=str(user_level), inline=True)
        embed.add_field(name="XP Durumu", value=f"{user_xp} / {needed_xp}", inline=True)
        embed.set_thumbnail(url=target.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="liderlik", description="Sunucunun en yüksek seviyeli üyelerini sıralar.")
    async def liderlik(self, interaction: discord.Interaction):
        self.data = load_data() # Güncel veriyi dosyadan çek
        
        if not self.data:
            await interaction.response.send_message("Henüz kayıtlı seviye verisi bulunmuyor.", ephemeral=True)
            return

        sorted_users = sorted(self.data.items(), key=lambda x: x[1]["xp"], reverse=True)[:10]
        
        embed = discord.Embed(title="Nexora - Liderlik Tablosu", color=discord.Color.blurple())
        
        description = ""
        for index, (u_id, stats) in enumerate(sorted_users, start=1):
            member = interaction.guild.get_member(int(u_id))
            name = member.display_name if member else "Bilinmeyen Üye"
            description += f"#{index} {name} — Seviye {stats['level']} ({stats['xp']} XP)\n"

        embed.description = description
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))