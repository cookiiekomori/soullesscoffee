from imports import *

class Profiles(commands.Cog):
    """Профили"""
    def __init__(self, bot, db_manager):
        self.bot = bot
        self.db_manager = db_manager

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Модуль {self.__class__.__name__} подключен.")

    def wrap_text(self, text, max_length, max_lines):
        lines = [text[i:i + max_length] for i in range(0, len(text), max_length)]
        return lines[:max_lines] 

    @commands.slash_command(name="set_about_me", description="Установить информацию о себе")
    async def set_about_me(self, ctx, *, about_me: str):
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        self.db_manager.update_user_data(guild_id, user_id, about_me=about_me)
        await ctx.send("Информация о себе успешно обновлена!", ephemeral=True)

    @commands.slash_command(name="profile", description="Показать профиль пользователя")
    async def profile(self, ctx, member: disnake.Member = None):
        if member is None:
            member = ctx.author

        user_data = self.db_manager.get_user_data(ctx.guild.id, member.id)
        if user_data is None:
            await ctx.send("Профиль не найден.")
            return

        # Загрузка фонового изображения
        custom_image_path = "C:\\Users\\cooki\\Pictures\\Adobe Images\\done\\Desiign_bot\\profile_design.png"
        custom_image = Image.open(custom_image_path)

        # Создаем новое изображение профиля с фоном
        profile_image = Image.new("RGBA", custom_image.size, (255, 255, 255, 0))  # Прозрачный фон
        profile_image.paste(custom_image, (0, 0))  # Накладываем фоновое изображение

        # Загрузка аватара
        avatar_url = str(member.avatar.url)
        avatar_response = requests.get(avatar_url)

        if avatar_response.status_code == 200:
            avatar = Image.open(io.BytesIO(avatar_response.content)).resize((160, 160))  # Размер аватарки

            mask = Image.new('L', (160, 160), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 160, 160), fill=255)

            avatar.putalpha(mask)
            profile_image.paste(avatar, (39, 29), avatar)  # Накладываем аватар на фон
        else:
            await ctx.send("Не удалось загрузить аватарку пользователя.")
            return


        draw = ImageDraw.Draw(profile_image)
        
        font_path = "fonts/Radiotechnika.otf"
        font_pathy = "fonts/AcuminR.otf"
        font = ImageFont.truetype(font_path, size=20)
        font_about = ImageFont.truetype(font_pathy, size=20)
        
        about_me = user_data['about_me']
        if not isinstance(about_me, str):
            about_me = "Я не я, корова не моя"
        wrapped_about_me = self.wrap_text(about_me, 25, 3)
        lvl = str(user_data['level']).zfill(3)
        nickname = member.display_name
        money = 34694
        joined_at = member.joined_at.strftime("%d-%m-%Y")

        formatted_nickname = nickname[:15]

        draw.text((248, 54), f"{formatted_nickname}", fill="white", font=font)
        for i, line in enumerate(wrapped_about_me):
            draw.text((248, 127 + i * 25), line, fill="white", font=font_about) 

        draw.text((443, 229), f"Level", fill="white", font=font)
        draw.text((450, 260), f"{lvl}", fill="white", font=font)
        draw.text((273, 229), f"Money", fill="white", font=font)
        draw.text((250, 260), f"{money}", fill="white", font=font)
        draw.text((40, 200), f"Дата присоединения", fill="white", font=ImageFont.truetype(font_path, size=10))
        draw.text((45, 215), f"{joined_at}", fill="white", font=font)
        
        user = await self.bot.fetch_user(member.id)
        is_active_developer = user.public_flags.active_developer
        is_early_verified_bot_developer = user.public_flags.early_verified_bot_developer
        is_verified_bot_developer = user.public_flags.verified_bot_developer

        if is_active_developer or is_verified_bot_developer or is_early_verified_bot_developer:
            additional_image_path = "C:\\Users\\cooki\\Pictures\\Adobe Images\\done\\Desiign_bot\\LOGO_prog.png" 
            if os.path.exists(additional_image_path):
                additional_image = Image.open(additional_image_path).resize((54, 54))
                profile_image.paste(additional_image, (25, 238), additional_image)  # Позиция изображения
            else:
                print(f"Изображение не найдено: {additional_image_path}")

        # Сохраняем изображение в буфер
        with io.BytesIO() as image_binary:
            profile_image.save(image_binary, 'PNG')
            image_binary.seek(0)
            await ctx.send(file=disnake.File(fp=image_binary, filename='profile.png'))

def setup(bot, db_manager):
    bot.add_cog(Profiles(bot, db_manager))
