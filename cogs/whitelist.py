import discord
from discord.ext import commands
from discord import ui
import asyncio

LOG_WL_ID = 1529606831800975482
CARGO_REMOVER = 1529575188394410204
CARGO_ADICIONAR = 1529575533028053184

class StaffWhitelistView(ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    @ui.button(label="Aprovar WL", style=discord.ButtonStyle.success, emoji="✅", custom_id="aprovar_wl")
    async def aprovar(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        member = guild.get_member(self.user_id)
        cargo_rem = guild.get_role(CARGO_REMOVER)
        cargo_add = guild.get_role(CARGO_ADICIONAR)

        if member:
            try:
                if cargo_rem and cargo_rem in member.roles:
                    await member.remove_roles(cargo_rem)
                if cargo_add:
                    await member.add_roles(cargo_add)

                embed_dm = discord.Embed(
                    title="✅ Whitelist Aprovada!",
                    description=f"Parabéns! Sua Whitelist no **{guild.name}** foi **APROVADA** por {interaction.user.mention}.",
                    color=discord.Color.green()
                )
                await member.send(embed=embed_dm)
            except Exception:
                pass

        for child in self.children:
            child.disabled = True

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.title += " [APROVADA]"
        embed.set_footer(text=f"Aprovado por: {interaction.user.name}")
        await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label="Reprovar WL", style=discord.ButtonStyle.danger, emoji="❌", custom_id="reprovar_wl")
    async def reprovar(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        member = guild.get_member(self.user_id)

        if member:
            try:
                embed_dm = discord.Embed(
                    title="❌ Whitelist Reprovada",
                    description=f"Sua Whitelist no **{guild.name}** foi **REPROVADA** por {interaction.user.mention}.",
                    color=discord.Color.red()
                )
                await member.send(embed=embed_dm)
            except Exception:
                pass

        for child in self.children:
            child.disabled = True

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.title += " [REPROVADA]"
        embed.set_footer(text=f"Reprovado por: {interaction.user.name}")
        await interaction.response.edit_message(embed=embed, view=self)


class WhitelistPanelView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Iniciar Whitelist", style=discord.ButtonStyle.success, emoji="📄", custom_id="iniciar_wl_btn")
    async def abrir_wl(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        user = interaction.user

        channel_name = f"wl-{user.name}".lower().replace(" ", "-")
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        if existing_channel:
            return await interaction.response.send_message(f"❌ Você já possui um canal aberto em {existing_channel.mention}!", ephemeral=True)

        category = discord.utils.get(guild.categories, name="Whitelists")
        if not category:
            category = await guild.create_category("Whitelists")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)
        await interaction.response.send_message(f"✅ Canal de Whitelist criado em {channel.mention}!", ephemeral=True)

        embed_inicio = discord.Embed(
            title="📄 Formulário de Whitelist",
            description=f"Olá {user.mention}! Responda às perguntas abaixo no chat para concluir sua Whitelist.\nVocê tem **5 minutos** para responder cada pergunta.",
            color=discord.Color.green()
        )
        embed_inicio.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        embed_inicio.set_footer(text=f"{guild.name} - Sistema de Whitelist", icon_url=guild.icon.url if guild.icon else None)
        await channel.send(embed=embed_inicio)

        perguntas = [
            ("1. Qual nome do seu personagem e ID?", "Exemplo: Martin, 27"),
            ("2. O que significa Roleplay?", "Exemplo: Role com os Amigos."),
            ("3. O que é Combat Logging?", "Exemplo: Combat Logging consiste em chingar um staff."),
            ("4. O que significa AMOR A VIDA?", "Exemplo: Reagir a um assalto."),
            ("5. O que é anti RP?", "Exemplo: É você fazer rp de bandido.")
        ]

        respostas = {}
        bot = interaction.client

        def check_text(m):
            return m.author == user and m.channel == channel

        try:
            for campo, pergunta in perguntas:
                embed_p = discord.Embed(
                    title=f"📝 {campo}",
                    description=f"*{pergunta}*",
                    color=discord.Color.green()
                )
                embed_p.set_author(name=user.display_name, icon_url=user.display_avatar.url)
                await channel.send(embed=embed_p)

                msg = await bot.wait_for("message", check=check_text, timeout=300.0)
                respostas[campo] = msg.content

        except asyncio.TimeoutError:
            await channel.send("⏰ Tempo esgotado! Você demorou mais de 5 minutos para responder. Este canal será excluído em 10 segundos...")
            await asyncio.sleep(10)
            return await channel.delete()

        log_channel = guild.get_channel(LOG_WL_ID)
        if log_channel:
            embed_log = discord.Embed(
                title=f"📄 Whitelist para Análise",
                color=discord.Color.gold()
            )
            embed_log.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            embed_log.set_thumbnail(url=user.display_avatar.url)
            embed_log.add_field(name="👤 Usuário", value=f"{user.mention} (`{user.id}`)", inline=False)
            for k, v in respostas.items():
                embed_log.add_field(name=k, value=v, inline=False)

            await log_channel.send(embed=embed_log, view=StaffWhitelistView(user.id))

        await channel.send("✅ Sua Whitelist foi enviada para análise! Canal fechando em 10 segundos...")
        await asyncio.sleep(10)
        await channel.delete()


class WhitelistCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_whitelist(self, ctx):
        embed = discord.Embed(
            title="🔔 WHITELIST",
            description="Clique no botão abaixo para iniciar o seu formulário de Whitelist.",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"{ctx.guild.name} - todos os direitos reservados.", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        await ctx.send(embed=embed, view=WhitelistPanelView())

async def setup(bot):
    bot.add_view(WhitelistPanelView())
    await bot.add_cog(WhitelistCog(bot))