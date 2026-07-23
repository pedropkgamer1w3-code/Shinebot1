import os discord
from discord.ext import commands
import os

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f'Cog carregada: {filename}')
                except commands.ExtensionAlreadyLoaded:
                    pass
                except Exception as e:
                    print(f'Erro ao carregar {filename}: {e}')

bot = MyBot()

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.event
async def on_command_error(ctx, error):
    print(f'Erro no comando "{ctx.command}": {error}')

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

if TOKEN:
    bot.run(TOKEN)
else:
    print("ERRO: Variável DISCORD_BOT_TOKEN não encontrada!")