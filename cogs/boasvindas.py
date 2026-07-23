import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import aiohttp

WELCOME_CHANNEL_ID = 1529530385304653964

class BoasVindas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return

        # 1. criar a imagem base (600x400) em preto e branco
        W, H = 600, 400
        bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(bg)

        # retângulos do fundo (tema preto e branco)
        draw.rounded_rectangle([70, 40, 510, 360], radius=30, fill=(30, 30, 30))
        draw.rounded_rectangle([90, 60, 530, 380], radius=30, fill=(200, 200, 200))
        draw.rounded_rectangle([80, 80, 520, 370], radius=30, fill=(15, 15, 15))

        # pill de topo (membro #count)
        draw.rounded_rectangle([200, 95, 400, 125], radius=10, fill=(35, 35, 35))
        
        try:
            font_small = ImageFont.truetype("arial.ttf", 16)
            font_big = ImageFont.truetype("arialbd.ttf", 24)
            font_italic = ImageFont.truetype("ariali.ttf", 16)
        except:
            font_small = font_big = font_italic = ImageFont.load_default()

        # texto da pill
        count_text = f"Membro #{member.guild.member_count}"
        draw.text((300, 110), count_text, fill=(200, 200, 200), font=font_small, anchor="mm")

        # 2. baixar e cortar avatar em círculo
        async with aiohttp.ClientSession() as session:
            async with session.get(member.display_avatar.url) as resp:
                if resp.status == 200:
                    avatar_data = await resp.read()
                    avatar_img = Image.open(io.BytesIO(avatar_data)).convert("RGBA")
                    
                    size = (110, 110)
                    avatar_img = avatar_img.resize(size, Image.Resampling.LANCZOS)
                    
                    mask = Image.new("L", size, 0)
                    mask_draw = ImageDraw.Draw(mask)
                    mask_draw.ellipse((0, 0) + size, fill=255)
                    
                    output_avatar = ImageOps.fit(avatar_img, mask.size, centering=(0.5, 0.5))
                    output_avatar.putalpha(mask)

                    # borda branca em volta da foto
                    draw.ellipse((242, 137, 358, 253), fill=(255, 255, 255))
                    bg.paste(output_avatar, (245, 140), output_avatar)

        # 3. textos da imagem
        draw.text((300, 275), f"Bem-vindo(a) ! {member.display_name}", fill=(255, 255, 255), font=font_big, anchor="mm")
        draw.text((300, 305), "ao", fill=(200, 200, 200), font=font_italic, anchor="mm")
        draw.text((300, 330), "Shine RolePlay !", fill=(255, 255, 255), font=font_big, anchor="mm")

        # salvar na memoria
        buffer = io.BytesIO()
        bg.save(buffer, format="PNG")
        buffer.seek(0)

        # 4. enviar texto e imagem
        msg_text = f"│ **Bem-vindo** {member.mention} **ao 📑 Shine RolePlay ✦!**"
        
        file = discord.File(buffer, filename="welcome.png")
        await channel.send(content=msg_text, file=file)

async def setup(bot):
    await bot.add_cog(BoasVindas(bot))