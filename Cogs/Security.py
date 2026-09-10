import discord
from discord.ext import commands
import datetime
import re

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.msg_cache = {}
        # Discord davet linklerini tespit eden Regex
        self.invite_regex = re.compile(r'(https?://)?(www\.)?(discord\.(gg|io|me|li|link|plus)|discordapp\.com/invite|discord\.com/invites)/\w+', re.IGNORECASE)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Yeni Hesap Koruması (Hesap açılışı 3 günden küçükse engelle)
        created_at = member.created_at
        now = datetime.datetime.now(datetime.timezone.utc)
        account_age_days = (now - created_at).days

        if account_age_days < 3:
            try:
                await member.send("Nexora sunucusunun güvenlik kuralları gereği çok yeni açılmış hesaplar sunucuya kabul edilmemektedir.")
            except:
                pass
            await member.kick(reason="Yeni açılmış şüpheli hesap (Anti-Raid)")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        # Yönetici ise güvenlik filtrelerinden muaf tut
        if message.author.guild_permissions.administrator:
            return

        # 1. Reklam ve Davet Linki Koruması
        if self.invite_regex.search(message.content):
            try:
                await message.delete()
                warning_msg = await message.channel.send(
                    f"{message.author.mention}, bu sunucuda reklam veya davet linki paylaşmak yasaktır!",
                    delete_after=5
                )
            except:
                pass
            return

        # 2. Spam Koruması (Hızlı mesaj kontrolü)
        author_id = message.author.id
        current_time = datetime.datetime.now().timestamp()
        
        if author_id in self.msg_cache:
            last_time, count = self.msg_cache[author_id]
            if current_time - last_time < 2:  # 2 saniyeden kısa sürede mesaj atıldıysa
                self.msg_cache[author_id] = (current_time, count + 1)
                if count >= 4:  # Hızlı mesaj sınırı
                    try:
                        await message.delete()
                        await message.channel.send(f"{message.author.mention} lütfen spam yapmayın.", delete_after=5)
                    except:
                        pass
                    return
            else:
                self.msg_cache[author_id] = (current_time, 1)
        else:
            self.msg_cache[author_id] = (current_time, 1)

async def setup(bot):
    await bot.add_cog(Security(bot))