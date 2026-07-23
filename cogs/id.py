import discord
from discord.ext import commands

CANAL_ID = 1529604934113169501

# cargos de id
CARGO_SEM_ID_ID = 1529574872345219312
CARGO_COM_ID_ID = 1529575354732380254

class RegistroID(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.proximo_id = 25  # comeca do 025

    @commands.command()
    async def id(self, ctx):
        # verifica se esta no canal correto
        if ctx.channel.id != CANAL_ID:
            return

        cargo_com_id = ctx.guild.get_role(CARGO_COM_ID_ID)

        # trava se ja tiver o cargo com id registrado
        if cargo_com_id and cargo_com_id in ctx.author.roles:
            embed_aviso = discord.Embed(
                description=f"⚠️ {ctx.author.mention}, você já possui um ID registrado e não pode usar este comando novamente!",
                color=discord.Color.yellow()
            )
            return await ctx.send(embed=embed_aviso)

        # formata o numero com zero a esquerda ex: 025, 026...
        id_formatado = f"{self.proximo_id:03d}"
        
        # novo apelido
        novo_nick = f"{id_formatado} | {ctx.author.display_name}"

        # limita o tamanho do nick pra nao estourar o limite do discord (32 caracteres)
        if len(novo_nick) > 32:
            novo_nick = novo_nick[:32]

        try:
            # altera o apelido
            await ctx.author.edit(nick=novo_nick)

            # resgata e troca os cargos
            cargo_sem_id = ctx.guild.get_role(CARGO_SEM_ID_ID)

            if cargo_sem_id and cargo_sem_id in ctx.author.roles:
                await ctx.author.remove_roles(cargo_sem_id)
            if cargo_com_id:
                await ctx.author.add_roles(cargo_com_id)
            
            embed = discord.Embed(
                description=f"✅ {ctx.author.mention} seu ID foi registrado com sucesso!\n**Novo nick:** `{novo_nick}`",
                color=discord.Color.green()
            )
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            embed.set_footer(text=f"ID registrado: {id_formatado}")
            
            await ctx.send(embed=embed)
            
            # avanca pro proximo id
            self.proximo_id += 1

        except discord.Forbidden:
            await ctx.send("❌ Eu não tenho permissão para alterar o seu apelido ou cargos! (O seu cargo pode ser maior que o meu).")
        except Exception as e:
            await ctx.send(f"❌ Ocorreu um erro ao registrar seu ID: {e}")

async def setup(bot):
    await bot.add_cog(RegistroID(bot))