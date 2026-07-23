import discord
from discord.ext import commands

class Utilitarios(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latência: `{latency}ms`")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def dm(self, ctx, member: discord.Member, *, mensagem: str):
        try:
            await member.send(mensagem)
            await ctx.send(f"✅ Mensagem enviada para {member.mention} na DM!")
        except:
            await ctx.send("❌ Não foi possível enviar mensagem na DM desse usuário.")

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="🤖 Central de Ajuda - Comandos do Bot",
            description="confira abaixo a lista completa de comandos disponíveis no servidor:",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🛠️ Moderação",
            value="`!ban @membro [motivo]` - bane um membro e avisa na dm\n"
                  "`!unban <id/tag> [motivo]` - desbane um membro e avisa na dm\n"
                  "`!baninfo <id/tag>` - mostra informações do banimento\n"
                  "`!kick @membro [motivo]` - expulsa um membro do servidor\n"
                  "`!mute @membro [minutos] [motivo]` - silencia um membro\n"
                  "`!unmute @membro` - remove o silenciamento do membro",
            inline=False
        )
        
        embed.add_field(
            name="💬 Gestão de Canais e Mensagens",
            value="`!clear <quantidade/all>` - apaga mensagens do canal\n"
                  "`!lock` - tranca o canal atual\n"
                  "`!unlock` - destranca o canal atual\n"
                  "`!slowmode <segundos>` - define o modo lento do canal\n"
                  "`!ticket` - envia o painel de atendimento\n"
                  "`!afk [motivo]` - ativa o modo AFK",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Utilitários",
            value="`!dm @membro <mensagem>` - envia uma mensagem privada pelo bot\n"
                  "`!ping` - testa a resposta do bot\n"
                  "`!help` - mostra esta lista de comandos",
            inline=False
        )
        
        embed.set_footer(text=f"Solicitado por {ctx.author.name}.", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utilitarios(bot))