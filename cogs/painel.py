import discord
from discord.ext import commands
from discord import ui

class PainelSelect(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Atendimento / Ticket",
                description="Enviar o painel de suporte e tickets neste canal",
                emoji="📩",
                value="ticket"
            ),
            discord.SelectOption(
                label="Whitelist",
                description="Enviar o painel de formulário de whitelist neste canal",
                emoji="🔔",
                value="whitelist"
            )
        ]
        super().__init__(
            placeholder="Escolha qual painel deseja enviar...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="painel_geral_select"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        escolha = self.values[0]
        channel = interaction.channel
        guild = interaction.guild

        if escolha == "ticket":
            try:
                import cogs.ticket as ticket_module
                ticket_view_cls = getattr(ticket_module, 'TicketView', None) or getattr(ticket_module, 'TicketPanelView', None)
                
                if ticket_view_cls is None:
                    await interaction.followup.send("❌ Não foi possível encontrar a View no arquivo cogs/ticket.py!", ephemeral=True)
                    return

                embed_ticket = discord.Embed(
                    title="📩 Central de Atendimento",
                    description="Selecione no menu abaixo a categoria do atendimento que você precisa:",
                    color=discord.Color.green()
                )
                embed_ticket.set_author(name=guild.name, icon_url=guild.icon.url if guild.icon else None)
                
                await channel.send(embed=embed_ticket, view=ticket_view_cls())
                await interaction.followup.send("✅ Painel de Atendimento/Ticket enviado com sucesso!", ephemeral=True)

            except Exception as e:
                await interaction.followup.send(f"❌ Erro ao enviar ticket: {e}", ephemeral=True)

        elif escolha == "whitelist":
            try:
                import cogs.whitelist as wl_module
                wl_view_cls = getattr(wl_module, 'WhitelistPanelView', None) or getattr(wl_module, 'WhitelistView', None)
                
                if wl_view_cls is None:
                    await interaction.followup.send("❌ Não foi possível encontrar a View no arquivo cogs/whitelist.py!", ephemeral=True)
                    return

                embed_wl = discord.Embed(
                    title="🔔 WHITELIST",
                    description="Clique no botão abaixo para iniciar o seu formulário de Whitelist.",
                    color=discord.Color.green()
                )
                embed_wl.set_footer(text=f"{guild.name} - todos os direitos reservados.", icon_url=guild.icon.url if guild.icon else None)
                
                await channel.send(embed=embed_wl, view=wl_view_cls())
                await interaction.followup.send("✅ Painel de Whitelist enviado com sucesso!", ephemeral=True)

            except Exception as e:
                await interaction.followup.send(f"❌ Erro ao enviar whitelist: {e}", ephemeral=True)


class PainelGeralView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PainelSelect())


class PainelGeralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="painel", aliases=["setup_painel"])
    async def painel_cmd(self, ctx):
        print(f"[LOG] Comando !painel executado por {ctx.author}")
        embed = discord.Embed(
            title="⚙️ Painel Geral de Configuração",
            description="Escolha no menu abaixo qual painel você deseja enviar neste canal:",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed, view=PainelGeralView())


async def setup(bot):
    bot.add_view(PainelGeralView())
    await bot.add_cog(PainelGeralCog(bot))