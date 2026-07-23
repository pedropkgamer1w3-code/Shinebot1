import discord
from discord.ext import commands
from datetime import timedelta

class Moderacao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1. BAN
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="não informado"):
        embed_dm = discord.Embed(
            title="🔨 Você foi banido!",
            description=f"Você foi banido do servidor **{ctx.guild.name}**.\n\n**Motivo:** {reason}",
            color=0xFF4500
        )

        dm_enviada = False
        try:
            await member.send(embed=embed_dm)
            dm_enviada = True
        except:
            dm_enviada = False

        try:
            await member.ban(reason=reason)
            msg = f'🚫 {member.mention} foi banido com sucesso! Motivo: {reason}'
            if not dm_enviada:
                msg += ' (DM fechada, aviso não entregue).'
            await ctx.send(msg)
        except discord.Forbidden:
            await ctx.send("❌ Não tenho permissão para banir esse membro!")

    # 2. UNBAN
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, id_ou_tag: str, *, reason="não informado"):
        banidos = [entry async for entry in ctx.guild.bans()]
        for ban_entry in banidos:
            user = ban_entry.user
            if str(user.id) == id_ou_tag or user.name == id_ou_tag or str(user) == id_ou_tag:
                await ctx.guild.unban(user, reason=reason)
                try:
                    embed_dm = discord.Embed(
                        title="✅ Você foi desbanido!",
                        description=f"Seu banimento no servidor **{ctx.guild.name}** foi removido.",
                        color=discord.Color.green()
                    )
                    await user.send(embed=embed_dm)
                except:
                    pass
                return await ctx.send(f'✅ {user.name} foi desbanido com sucesso!')
        await ctx.send('❌ Usuário não foi encontrado na lista de banidos!')

    # 3. BANINFO
    @commands.command()
    async def baninfo(self, ctx, id_ou_tag: str):
        banidos = [entry async for entry in ctx.guild.bans()]
        for ban_entry in banidos:
            user = ban_entry.user
            if str(user.id) == id_ou_tag or user.name == id_ou_tag or str(user) == id_ou_tag:
                embed = discord.Embed(
                    title=f"📋 Informações do banimento: {user.name}",
                    color=discord.Color.blue()
                )
                embed.set_author(name=str(user), icon_url=user.display_avatar.url)
                embed.add_field(name="Motivo", value=ban_entry.reason or "Nenhum motivo informado.", inline=False)
                embed.set_footer(text=f"ID: {user.id}")
                return await ctx.send(embed=embed)
        await ctx.send('❌ Usuário não foi encontrado na lista de banidos!')

    # 4. KICK
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="não informado"):
        try:
            embed_dm = discord.Embed(
                title="👞 Você foi expulso!",
                description=f"Você foi expulso do servidor **{ctx.guild.name}**.\n\n**Motivo:** {reason}",
                color=discord.Color.orange()
            )
            await member.send(embed=embed_dm)
        except:
            pass

        try:
            await member.kick(reason=reason)
            await ctx.send(f'👞 {member.mention} foi expulso do servidor!')
        except discord.Forbidden:
            await ctx.send("❌ Não tenho permissão para expulsar esse membro!")

    # 5. MUTE (TIMEOUT)
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, minutos: int, *, reason="não informado"):
        tempo = timedelta(minutes=minutos)
        try:
            await member.timeout(tempo, reason=reason)
            await ctx.send(f'🔇 {member.mention} foi silenciado por {minutos} minutos! Motivo: {reason}')
        except discord.Forbidden:
            await ctx.send("❌ Não tenho permissão para silenciar esse membro!")

    # 6. UNMUTE
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        try:
            await member.timeout(None)
            await ctx.send(f'🔊 Silenciamento de {member.mention} foi removido!')
        except discord.Forbidden:
            await ctx.send("❌ Não tenho permissão para remover o silenciamento desse membro!")

async def setup(bot):
    await bot.add_cog(Moderacao(bot))