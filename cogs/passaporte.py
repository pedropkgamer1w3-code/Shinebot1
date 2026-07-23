import discord
from discord.ext import commands
from discord import ui
import asyncio

LOG_PASSAPORTE_ID = 1529606877745516745
CARGO_SEM_PASSAPORTE = 1529575051119034388
CARGO_COM_PASSAPORTE = 1529575424164630669

class StaffPassaporteView(ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    @ui.button(label="Aprovar Passaporte", style=discord.ButtonStyle.success, emoji="✅", custom_id="aprovar_passaporte")
    async def aprovar(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        member = guild.get_member(self.user_id)

        cargo_sem = guild.get_role(CARGO_SEM_PASSAPORTE)
        cargo_com = guild.get_role(CARGO_COM_PASSAPORTE)

        if member:
            try:
                if cargo_sem and cargo_sem in member.roles:
                    await member.remove_roles(cargo_sem)
                if cargo_com:
                    await member.add_roles(cargo_com)

                embed_dm = discord.Embed(
                    title="✈️ Passaporte Aprovado!",
                    description=f"Parabéns! Seu Passaporte no **{guild.name}** foi **APROVADO** por {interaction.user.mention}.\nSeja bem-vindo e bom RP!",
                    color=discord.Color.green()
                )
                await member.send(embed=embed_dm)
            except Exception:
                pass

        for child in self.children:
            child.disabled = True

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.title += " [APROVADO]"
        embed.set_footer(text=f"Aprovado por: {interaction.user.name}")

        await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label="Reprovar Passaporte", style=discord.ButtonStyle.danger, emoji="❌", custom_id="reprovar_passaporte")
    async def reprovar(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        member = guild.get_member(self.user_id)

        if member:
            try:
                embed_dm = discord.Embed(
                    title="❌ Passaporte Reprovado",
                    description=f"Seu Passaporte no **{guild.name}** foi **REPROVADO** por {interaction.user.mention}.\nVocê pode solicitar novamente quando quiser!",
                    color=discord.Color.red()
                )
                await member.send(embed=embed_dm)
            except Exception:
                pass

        for child in self.children:
            child.disabled = True

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.title += " [REPROVADO]"
        embed.set_footer(text=f"Reprovado por: {interaction.user.name}")

        await interaction.response.edit_message(embed=embed, view=self)


class PassaportePanelView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Solicitar Passaporte", style=discord.ButtonStyle.primary, emoji="✈️", custom_id="iniciar_passaporte_btn")
    async def abrir_passaporte(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        user = interaction.user

        # Nome do canal: passaporte-nomedousuario
        channel_name = f"passaporte-{user.name}".lower().replace(" ", "-")
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        if existing_channel:
            return await interaction.response.send_message(f"❌ Você já possui um canal aberto em {existing_channel.mention}!", ephemeral=True)

        category = discord.utils.get(guild.categories, name="Passaportes")
        if not category:
            category = await guild.create_category("Passaportes")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)
        await interaction.response.send_message(f"✅ Canal de formulário criado em {channel.mention}!", ephemeral=True)

        embed_inicio = discord.Embed(
            title="✈️ Emissão de Passaporte",
            description=f"Olá {user.mention}! Você tem **15 minutos no total** para responder **todas** as perguntas abaixo neste canal.",
            color=discord.Color.blue()
        )
        embed_inicio.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        embed_inicio.set_footer(text=f"{guild.name} - Emissão de Passaporte", icon_url=guild.icon.url if guild.icon else None)
        await channel.send(embed=embed_inicio)

        perguntas = [
            ("1. Nome do Personagem", "Digite o nome e sobrenome do seu personagem:"),
            ("2. Data de Nascimento", "Digite a data de nascimento do seu personagem (Formato: `00/00/00`):"),
            ("3. Idade do Personagem", "Digite a idade do seu personagem (Formato: `0 anos` ou `00 anos`):"),
            ("4. História do Personagem", "Conte um pouco sobre a história do seu personagem:"),
            ("5. Foto do Personagem", "Envie uma **imagem/foto** do seu personagem (anexe no chat ou envie um link válido de imagem):")
        ]

        respostas = {}
        bot = interaction.client

        def check_text(m):
            return m.author == user and m.channel == channel

        def check_photo(m):
            return m.author == user and m.channel == channel and (len(m.attachments) > 0 or m.content.startswith("http"))

        try:
            tempo_total = 900.0
            inicio_formulario = asyncio.get_event_loop().time()

            for campo, pergunta in perguntas:
                embed_p = discord.Embed(
                    title=f"📝 {campo}",
                    description=pergunta,
                    color=discord.Color.dark_blue()
                )
                embed_p.set_author(name=user.display_name, icon_url=user.display_avatar.url)
                await channel.send(embed=embed_p)

                tempo_decorrido = asyncio.get_event_loop().time() - inicio_formulario
                tempo_restante = tempo_total - tempo_decorrido

                if tempo_restante <= 0:
                    raise asyncio.TimeoutError()

                if campo == "5. Foto do Personagem":
                    msg = await bot.wait_for("message", check=check_photo, timeout=tempo_restante)
                    if len(msg.attachments) > 0:
                        respostas[campo] = msg.attachments[0].url
                    else:
                        respostas[campo] = msg.content
                else:
                    msg = await bot.wait_for("message", check=check_text, timeout=tempo_restante)
                    respostas[campo] = msg.content

        except asyncio.TimeoutError:
            await channel.send("⏰ Tempo esgotado! Você demorou mais de 15 minutos para concluir o formulário. Este canal será excluído em 10 segundos...")
            await asyncio.sleep(10)
            return await channel.delete()

        log_channel = guild.get_channel(LOG_PASSAPORTE_ID)
        if log_channel:
            embed_log = discord.Embed(
                title=f"🛂 Solicitação de Passaporte",
                color=discord.Color.orange()
            )
            embed_log.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            embed_log.set_thumbnail(url=user.display_avatar.url)
            embed_log.add_field(name="👤 Usuário", value=f"{user.mention} (`{user.id}`)", inline=False)
            embed_log.add_field(name="📛 Nome do Personagem", value=respostas["1. Nome do Personagem"], inline=False)
            embed_log.add_field(name="📅 Data de Nascimento", value=respostas["2. Data de Nascimento"], inline=True)
            embed_log.add_field(name="🎂 Idade", value=respostas["3. Idade do Personagem"], inline=True)
            embed_log.add_field(name="📖 História", value=respostas["4. História do Personagem"], inline=False)
            
            if respostas["5. Foto do Personagem"].startswith("http"):
                embed_log.set_image(url=respostas["5. Foto do Personagem"])

            await log_channel.send(embed=embed_log, view=StaffPassaporteView(user.id))

        await channel.send("✅ Seu formulário foi enviado com sucesso para a equipe de análise! Este canal será fechado em 10 segundos...")
        await asyncio.sleep(10)
        await channel.delete()


class Passaporte(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_passaporte(self, ctx):
        embed = discord.Embed(
            title="✈️ Emissão de Passaporte",
            description="Clique no botão abaixo para abrir o formulário de emissão do seu passaporte.",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"{ctx.guild.name} - todos os direitos reservados.", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        await ctx.send(embed=embed, view=PassaportePanelView())

async def setup(bot):
    bot.add_view(PassaportePanelView())
    await bot.add_cog(Passaporte(bot))