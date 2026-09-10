import discord
from discord.ext import commands
from discord import app_commands

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Siyah, Beyaz, Kırmızı, Mavi, Sarı ve en altta Pembe renk rol ID'leri
        self.role_mapping = {
            "⚫": 1545886656907837570,  # Siyah
            "⚪": 1545886936168661062,  # Beyaz
            "🔴": 1545885745724522648,  # Kırmızı
            "🔵": 1542606681815650504,  # Mavi
            "🟡": 1545886131592106066,  # Sarı
            "🩷": 1542606764262953031,   # Pembe (En altta)
        }
        
        self.target_message_id = 1547593407793205319 

    @app_commands.command(name="kurulum", description="Renk rolleri seçim mesajını gönderir.")
    @app_commands.checks.has_permissions(administrator=True)
    async def kurulum(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎨 Renk Rolleri",
            description="Aşağıdaki renkli emojilere basarak istediğin **tek bir** renk rolünü alabilirsin!\n*(Başka bir renge basarsan eski rengin otomatik değiştirilir.)*",
            color=0x9b59b6
        )
        
        await interaction.response.send_message("Renk menüsü hazırlanıyor...", ephemeral=True)
        msg = await interaction.channel.send(embed=embed)
        self.target_message_id = msg.id
        
        for emoji in self.role_mapping.keys():
            await msg.add_reaction(emoji)
            
        await interaction.edit_original_response(content=f"Kurulum tamamlandı! Hedef Mesaj ID: `{msg.id}`")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id or payload.message_id != self.target_message_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        emoji_str = str(payload.emoji)
        if emoji_str in self.role_mapping:
            member = guild.get_member(payload.user_id)
            if not member:
                return

            # Kullanıcının üzerindeki diğer TÜM renk rollerini al (Tek renk kuralı)
            all_color_role_ids = list(self.role_mapping.values())
            roles_to_remove = [guild.get_role(r_id) for r_id in all_color_role_ids if guild.get_role(r_id) in member.roles]
            
            if roles_to_remove:
                try:
                    await member.remove_roles(*roles_to_remove)
                except discord.Forbidden:
                    pass

            # Seçtiği yeni rengi ver
            role_id = self.role_mapping[emoji_str]
            role = guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role)
                except discord.Forbidden:
                    pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.message_id != self.target_message_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        emoji_str = str(payload.emoji)
        if emoji_str in self.role_mapping:
            role_id = self.role_mapping.get(emoji_str)
            if role_id:
                role = guild.get_role(role_id)
                member = guild.get_member(payload.user_id)
                
                if role and member:
                    try:
                        await member.remove_roles(role)
                    except discord.Forbidden:
                        pass

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))