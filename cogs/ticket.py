import discord
from discord.ext import commands
from discord import ui
import asyncio
import io

CATEGORIA_ID = 1529630087140343823
LOG_CHANNEL_ID = 1529230676786942033

class TicketSelect(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Dúvidas",
                description="Tire suas dúvidas com a equipe de suporte",
                emoji="❓",
                value="duvidas"
            ),
            discord.SelectOption(
                label="Denúncias",
                description="Faça uma denúncia sobre algo do servidor",
                emoji="🚨",
                value="denuncias"
            ),
            discord.SelectOption(
                label="Outros",
                description="Outros assuntos com a administração",
                emoji="📌",
                value="outros"
            )
        ]
        super().__init__(
            placeholder="Selecione a categoria do atendimento...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_select_category"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        user = interaction.user
        categoria_nome = self.values[0]

        channel_name = f"ticket-{categoria_nome}-{user.name}".lower()

        existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
        if existing_channel:
            await interaction.followup.send(f"❌ vc já tem um ticket aberto em {existing_channel.mention}!", ephemeral=True)
            return

        category = guild.get_channel(CATEGORIA_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            reason=f"Ticket aberto por {user}"
        )

        embed = discord.Embed(
            title=f"📩 Atendimento - {categoria_nome.upper()}",
            description=f"olá {user.mention}, bem-vindo ao seu ticket!\naguarde um membro da equipe responder.\n\nclique no botão abaixo para fechar o ticket.",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"{guild.name} • Suporte", icon_url=guild.icon.url if guild.icon else None)

        await ticket_channel.send(content=f"{user.mention}", embed=embed, view=OpenTicketView(user.id))
        await interaction.followup.send(f"✅ ticket criado com sucesso em {ticket_channel.mention}!", ephemeral=True)

        # envia log de criação
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="📥 Ticket Aberto",
                description=f"**Canal:** {ticket_channel.mention}\n**Autor:** {user.mention} (`{user.id}`)\n**Categoria:** {categoria_nome}",
                color=discord.Color.green()
            )
            await log_channel.send(embed=log_embed)


class OpenTicketView(ui.View):
    def __init__(self, owner_id: int):
        super().__init__(timeout=None)
        self.owner_id = owner_id

    @ui.button(label="Fechar Ticket", style=discord.ButtonStyle.red, emoji="🔒", custom_id="btn_close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        channel = interaction.channel
        guild = interaction.guild

        owner = guild.get_member(self.owner_id)
        if owner:
            await channel.set_permissions(owner, read_messages=False, send_messages=False)

        embed = discord.Embed(
            title="🔒 Ticket Fechado",
            description=f"ticket fechado por {interaction.user.mention}.\nescolha uma das opções abaixo para gerenciar:",
            color=discord.Color.gold()
        )

        await channel.send(embed=embed, view=ClosedTicketView(self.owner_id))

        # envia log de fechamento
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="🔒 Ticket Fechado",
                description=f"**Canal:** {channel.name}\n**Fechado por:** {interaction.user.mention}",
                color=discord.Color.gold()
            )
            await log_channel.send(embed=log_embed)


class ClosedTicketView(ui.View):
    def __init__(self, owner_id: int):
        super().__init__(timeout=None)
        self.owner_id = owner_id

    @ui.button(label="Reabrir", style=discord.ButtonStyle.green, emoji="🔓", custom_id="btn_reopen_ticket")
    async def reopen_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        channel = interaction.channel
        guild = interaction.guild

        owner = guild.get_member(self.owner_id)
        if owner:
            await channel.set_permissions(owner, read_messages=True, send_messages=True, attach_files=True)

        embed = discord.Embed(
            title="🔓 Ticket Reaberto",
            description=f"ticket reaberto por {interaction.user.mention}.",
            color=discord.Color.green()
        )
        await channel.send(embed=embed)

        # envia log de reabertura
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="🔓 Ticket Reaberto",
                description=f"**Canal:** {channel.name}\n**Reaberto por:** {interaction.user.mention}",
                color=discord.Color.blue()
            )
            await log_channel.send(embed=log_embed)

    @ui.button(label="Transcript", style=discord.ButtonStyle.blurple, emoji="📄", custom_id="btn_transcript_ticket")
    async def transcript_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        channel = interaction.channel

        transcript_text = f"--- TRANSCRIPT DO TICKET: {channel.name} ---\n\n"
        
        async for msg in channel.history(limit=None, oldest_first=True):
            time_str = msg.created_at.strftime("%d/%m/%Y %H:%M:%S")
            transcript_text += f"[{time_str}] {msg.author} ({msg.author.id}): {msg.content}\n"

        file_data = io.BytesIO(transcript_text.encode('utf-8'))
        discord_file = discord.File(file_data, filename=f"transcript-{channel.name}.txt")

        await interaction.followup.send("📄 aqui está o transcript das mensagens:", file=discord_file, ephemeral=True)

    @ui.button(label="Deletar", style=discord.ButtonStyle.red, emoji="⛔", custom_id="btn_delete_ticket")
    async def delete_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("🗑️ este ticket será deletado em 5 segundos...", ephemeral=False)
        
        channel = interaction.channel
        guild = interaction.guild

        # envia log de deleção
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="🗑️ Ticket Deletado",
                description=f"**Canal:** {channel.name}\n**Deletado por:** {interaction.user.mention}",
                color=discord.Color.red()
            )
            await log_channel.send(embed=log_embed)

        await asyncio.sleep(5)
        await channel.delete()


class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setup_ticket")
    @commands.has_permissions(administrator=True)
    async def setup_ticket_cmd(self, ctx):
        embed = discord.Embed(
            title="📩 Central de Atendimento",
            description="Selecione no menu abaixo a categoria do atendimento que você precisa:",
            color=discord.Color.green()
        )
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        await ctx.send(embed=embed, view=TicketView())


async def setup(bot):
    bot.add_view(TicketView())
    await bot.add_cog(TicketCog(bot))