import discord
from discord import app_commands
from discord.ext import commands
import wavelink

# --- İNTERAKTİF BUTON ARAYÜZÜ ---
class MusicPlayerView(discord.ui.View):
    def __init__(self, player: wavelink.Player):
        super().__init__(timeout=None)
        self.player = player

    @discord.ui.button(label="⏯️ Durdur / Devam Et", style=discord.ButtonStyle.primary)
    async def pause_resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.voice or interaction.user.voice.channel != self.player.channel:
            return await interaction.response.send_message("Müziği kontrol etmek için botla aynı ses kanalında olmalısın!", ephemeral=True)

        if self.player.paused:
            await self.player.pause(False)
            await interaction.response.send_message("▶️ Müzik devam ettiriliyor...", ephemeral=True)
        else:
            await self.player.pause(True)
            await interaction.response.send_message("⏸️ Müzik duraklatıldı.", ephemeral=True)

    @discord.ui.button(label="⏭️ Geç", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.voice or interaction.user.voice.channel != self.player.channel:
            return await interaction.response.send_message("Müziği kontrol etmek için botla aynı ses kanalında olmalısın!", ephemeral=True)

        await self.player.skip()
        await interaction.response.send_message("⏭️ Şarkı geçildi!", ephemeral=True)

    @discord.ui.button(label="⏹️ Bitir ve Çık", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.voice or interaction.user.voice.channel != self.player.channel:
            return await interaction.response.send_message("Müziği kontrol etmek için botla aynı ses kanalında olmalısın!", ephemeral=True)

        await self.player.disconnect()
        await interaction.response.send_message("⏹️ Müzik durduruldu ve kanaldan çıkıldı.", ephemeral=True)


# --- MÜZİK MODÜLÜ ---
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        # Modül yüklendiğinde otomatik Lavalink müzik motoruna bağlanır
        if not wavelink.Pool.nodes:
            node = wavelink.Node(uri="http://ssl.freelavalink.com:443", password="www.freelavalink.com")
            await wavelink.Pool.connect(nodes=[node], client=self.bot)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        print(f"Lavalink Müzik Sunucusu Bağlandı: {payload.node.identifier}")

    @app_commands.command(name="play", description="Spotify/YouTube bağlantısı veya şarkı adı ile müzik çalar.")
    async def play(self, interaction: discord.Interaction, sorgu: str):
        if not interaction.user.voice:
            return await interaction.response.send_message("Önce bir ses kanalına katılmalısın!", ephemeral=True)

        await interaction.response.defer()

        # Ses kanalına bağlan
        if not interaction.guild.voice_client:
            player: wavelink.Player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
        else:
            player: wavelink.Player = interaction.guild.voice_client

        # Şarkıyı veya Spotify linkini ara
        tracks: wavelink.Search = await wavelink.Playable.search(sorgu)
        if not tracks:
            return await interaction.followup.send("Aradığın şarkı veya link bulunamadı!")

        track: wavelink.Playable = tracks[0]
        await player.queue.put_wait(track)

        if not player.playing:
            await player.play(player.queue.get())

        # --- ARAYÜZ (EMBED + BUTONLAR) ---
        embed = discord.Embed(
            title="🎶 Şu An Çalıyor",
            description=f"**[{track.title}]({track.uri})**",
            color=0x9b59b6
        )
        if track.artwork:
            embed.set_thumbnail(url=track.artwork)

        embed.add_field(name="Sanatçı / Kanal", value=track.author, inline=True)
        embed.add_field(name="Süre", value=f"{int(track.length / 1000 // 60)}:{int(track.length / 1000 % 60):02d}", inline=True)
        embed.add_field(name="İsteyen", value=interaction.user.mention, inline=True)

        # Butonlu Arayüzü Gönder
        view = MusicPlayerView(player)
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="leave", description="Botu ses kanalından çıkarır.")
    async def leave(self, interaction: discord.Interaction):
        player: wavelink.Player = interaction.guild.voice_client
        if player:
            await player.disconnect()
            await interaction.response.send_message("👋 Ses kanalından ayrıldım.")
        else:
            await interaction.response.send_message("Zaten bir ses kanalında değilim.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Music(bot))