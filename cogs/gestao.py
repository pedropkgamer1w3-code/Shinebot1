import discord
from discord.ext import commands

class Gestao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1. CLEAR
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: str):
        if amount.lower() == "all":
            deleted = await ctx.channel.purge(limit=100)
            await ctx.send(f'🧹 {len(deleted)-1} mensagens apagadas com sucesso!', delete_after=5)
        else:
            try:
                qtd = int(amount)
                await ctx.channel.purge(limit=qtd + 1)
                await ctx.send(f'🧹 {qtd} mensagens apagadas com sucesso!', delete_after=5)
            except ValueError:
                await ctx.send('❌ Digite um número válido ou `all`! Ex: `!clear 10` ou `!clear all`')

    # 2. LOCK
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        
        embed = discord.Embed(
            description="🔒 Canal trancado com sucesso!",
            color=discord.Color.red()
        )
        embed.set_author(
            name=ctx.guild.name, 
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        embed.set_footer(text=f"ID do canal: {ctx.channel.id}")
        
        await ctx.send(embed=embed)

    # 3. UNLOCK
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        
        embed = discord.Embed(
            description="🔓 Canal destrancado com sucesso!",
            color=discord.Color.green()
        )
        embed.set_author(
            name=ctx.guild.name, 
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        embed.set_footer(text=f"ID do canal: {ctx.channel.id}")
        
        await ctx.send(embed=embed)

    # 4. SLOWMODE
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, segundos: int):
        await ctx.channel.edit(slowmode_delay=segundos)
        await ctx.send(f"⏱️ Modo lento definido para {segundos} segundos!")

async def setup(bot):
    await bot.add_cog(Gestao(bot))