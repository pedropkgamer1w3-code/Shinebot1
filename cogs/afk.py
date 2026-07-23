import discord
from discord.ext import commands

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_users = {}

    @commands.command()
    async def afk(self, ctx, *, motivo="Nenhum motivo informado."):
        self.afk_users[ctx.author.id] = motivo
        await ctx.reply("🦇 | Modo AFK ativado! Para a sua conveniência, o modo AFK será automaticamente desativado quando você falar algo no chat!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Se o usuario que esta AFK falar algo, remove do AFK
        if message.author.id in self.afk_users:
            del self.afk_users[message.author.id]
            await message.reply(f"🦇 | Bem-vindo de volta, {message.author.mention}! Seu AFK foi removido.", delete_after=5)

        # Se alguem mencionar um usuario que esta AFK
        for mention in message.mentions:
            if mention.id in self.afk_users:
                motivo = self.afk_users[mention.id]
                await message.reply(f"🦇 | {mention.mention} está AFK! Motivo: {motivo}")

async def setup(bot):
    await bot.add_cog(AFK(bot))