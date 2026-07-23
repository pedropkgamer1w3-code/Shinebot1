import discord
from discord.ext import commands

LOG_CHANNEL_ID = 1529213861159370936
MESSAGE_LOG_CHANNEL_ID = 1529213794566537227

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        channel = guild.get_channel(LOG_CHANNEL_ID)
        if not channel:
            return
        embed = discord.Embed(
            title=f"🚫 {user.name} foi banido!",
            color=discord.Color.green()
        )
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)
        embed.set_footer(text=f"ID do usuário: {user.id}")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        channel = message.guild.get_channel(MESSAGE_LOG_CHANNEL_ID)
        if not channel:
            return
        embed = discord.Embed(
            title="🗑️ Mensagem Apagada",
            description=f"**Autor:** {message.author.mention}\n**Canal:** {message.channel.mention}\n**Conteúdo:** {message.content or 'Sem texto'}",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"ID do Autor: {message.author.id}")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        channel = before.guild.get_channel(MESSAGE_LOG_CHANNEL_ID)
        if not channel:
            return
        embed = discord.Embed(
            title="✏️ Mensagem Editada",
            description=f"**Autor:** {before.author.mention}\n**Canal:** {before.channel.mention}\n\n**Antes:** {before.content}\n**Depois:** {after.content}",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"ID do Autor: {before.author.id}")
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Logs(bot))