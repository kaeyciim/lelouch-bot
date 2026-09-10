import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sil", description="Belirtilen miktarda mesajı temizler.")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.has_permissions(manage_messages=True)
    async def sil(self, interaction: discord.Interaction, adet: int):
        if adet < 1 or adet > 100:
            await interaction.response.send_message("Lütfen 1 ile 100 arasında bir sayı girin.", ephemeral=True)
            return

        # Zaman aşımı hatasını (404 Unknown Interaction) önlemek için defer kullanıyoruz
        await interaction.response.defer(ephemeral=True)

        deleted = await interaction.channel.purge(limit=adet)
        await interaction.followup.send(f"**{len(deleted)}** mesaj temizlendi.", ephemeral=True)

    @app_commands.command(name="mute", description="Üyeyi belirli bir süre (dakika) susturur.")
    @app_commands.default_permissions(moderate_members=True)
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, üye: discord.Member, dakika: int, sebep: str = "Belirtilmedi"):
        duration = timedelta(minutes=dakika)
        await üye.timeout(duration, reason=sebep)
        await interaction.response.send_message(f"{üye.mention} **{dakika} dakika** boyunca susturuldu. (Sebep: {sebep})")

    @app_commands.command(name="kick", description="Üyeyi sunucudan atar.")
    @app_commands.default_permissions(kick_members=True)
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, üye: discord.Member, sebep: str = "Belirtilmedi"):
        await üye.kick(reason=sebep)
        await interaction.response.send_message(f"{üye.mention} sunucudan atıldı. (Sebep: {sebep})")

    @app_commands.command(name="ban", description="Üyeyi sunucudan yasaklar.")
    @app_commands.default_permissions(ban_members=True)
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, üye: discord.Member, sebep: str = "Belirtilmedi"):
        await üye.ban(reason=sebep)
        await interaction.response.send_message(f"{üye.mention} sunucudan yasaklandı. (Sebep: {sebep})")

    @app_commands.command(name="kurallar", description="Nexora sunucu kurallarını gönderir.")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def kurallar(self, interaction: discord.Interaction):
        # 1. Komutu yazan kişiye gizli mesaj gönderip komut logunu ortadan kaldırıyoruz
        await interaction.response.send_message("Kurallar başarıyla gönderildi.", ephemeral=True)
        
        # 2. Yerel dosyayı tanıtıyoruz
        resim_dosyasi = discord.File("kurallar.png", filename="kurallar.png")
        
        embed = discord.Embed(
            title="✨ N E X O R A  —  K U R A L L A R",
            description=(
                "Sunucumuzun huzurunu ve düzenini korumak adına aşağıdaki kurallara tüm üyelerimizin uyması zorunludur.\n\n"
                "🔹 **1. Saygılı Olun:** Din, dil, ırk ve siyaset tartışması yapmak; küfür, hakaret ve aşağılama kesinlikle yasaktır.\n\n"
                "🔹 **2. Kibar Olun:** Yanlış bilgi veren birini görürseniz aşağılamak yerine kibarca doğrusunu anlatın.\n\n"
                "🔹 **3. Gizliliğe Uyun:** Kimsenin kişisel bilgisini (telefon, fotoğraf vb.) izinsiz paylaşmayın.\n\n"
                "🔹 **4. Kavga Etmeyin:** Kişisel tartışmalarınızı ve hesaplaşmalarınızı özel mesajdan (DM) halledin.\n\n"
                "🔹 **5. Bağırmayın ve Spam Yapmayın:** Büyük harfle yazmak bağırmak demektir, yapmayın. Sohbeti gereksiz mesajlarla kirletmeyin.\n\n"
                "🔹 **6. Yetkililere Haber Verin:** Kural dışı bir durum görürseniz lütfen yetkililere bildirin.\n\n"
                "⚠️ *Her kural yazılı olmak zorunda değildir ve sunucuya giren tüm üyeler kuralları okumuş kabul edilir.*"
            ),
            color=0x9b59b6
        )
        
        # 3. Embed içine resmi dosya eki olarak (attachment) yerleştiriyoruz
        embed.set_image(url="attachment://kurallar.png")
        
        # 4. Kanala gönderirken hem embed'i hem de dosyayı aynı anda iletiyoruz
        await interaction.channel.send(file=resim_dosyasi, embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))