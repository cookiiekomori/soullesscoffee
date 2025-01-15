from imports import *

# Функция для загрузки конфигурации
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Загрузка конфигурации
settings = load_config()

class Embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.developer_role_id = settings['roles']['developer']['role_id']
        self.admin_role_id = settings['roles']['admin']['role_id']

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Модуль {self.__class__.__name__} подключен.")

    def is_valid_url(self, url):
        """Проверяет, является ли строка действительным URL."""
        return url is not None and (url.startswith("http://") or url.startswith("https://"))

    @commands.slash_command(description="Создать эмбед из JSON")
    async def create_embed(self, inter: disnake.CommandInteraction, json_data: str):
        try:
            # Парсим JSON-строку
            data = json.loads(json_data)

            # Получаем информацию о взаимодействии
            author = inter.user
            guild = inter.guild
            member = guild.get_member(author.id) if guild else None
            bot_avatar = self.bot.user.avatar.url if self.bot.user.avatar else None

            # Создаем эмбед
            embed = disnake.Embed(
                title=self.replace_variables(data.get('title'), author, guild, member),
                description=self.replace_variables(data.get('description'), author, guild, member),
                url=self.replace_variables(data.get('url'), author, guild, member),
                color=self.get_color(data.get('color')),
                timestamp=self.parse_timestamp(data.get('timestamp'))
            )

            # Добавляем footer, если он есть
            if 'footer' in data:
                footer_data = data['footer']
                if 'text' not in footer_data:
                    await inter.response.send_message("Ошибка: У футера отсутствует текст.", ephemeral=True)
                    return
                footer_icon_url = self.replace_variables(footer_data.get('icon_url', bot_avatar), author, guild, member)
                embed.set_footer(
                    text=self.replace_variables(footer_data['text'], author, guild, member),
                    icon_url=footer_icon_url if self.is_valid_url(footer_icon_url) else None
                )

            # Добавляем thumbnail, если он есть
            if 'thumbnail' in data:
                thumbnail_url = self.replace_variables(data['thumbnail']['url'], author, guild, member)
                if self.is_valid_url(thumbnail_url):
                    embed.set_thumbnail(url=thumbnail_url)

            # Добавляем image, если он есть
            if 'image' in data:
                image_url = self.replace_variables(data['image']['url'], author, guild, member)
                if self.is_valid_url(image_url):
                    embed.set_image(url=image_url)

            # Добавляем author, если он есть
            if 'author' in data:
                author_data = data['author']
                if 'name' not in author_data:
                    await inter.response.send_message("Ошибка: У автора отсутствует имя.", ephemeral=True)
                    return
                author_icon_url = self.replace_variables(author_data.get('icon_url', author.avatar.url if author.avatar else None), author, guild, member)
                embed.set_author(
                    name=self.replace_variables(author_data['name'], author, guild, member),
                    url=self.replace_variables(author_data.get('url'), author, guild, member),
                    icon_url=author_icon_url if self.is_valid_url(author_icon_url) else None
                )

            # Добавляем поля, если они есть
            if 'fields' in data:
                for field in data['fields']:
                    embed.add_field(
                        name=self.replace_variables(field['name'], author, guild, member),
                        value=self.replace_variables(field['value'], author, guild, member),
                        inline=field.get('inline', False)
                    )

            # Отправляем сообщение с эмбед
            await inter.response.send_message(content=self.replace_variables(data.get('content', ''), author, guild, member), embed=embed)

        except json.JSONDecodeError:
            await inter.response.send_message("Ошибка: Неверный формат JSON.", ephemeral=True)
        except Exception as e:
            await inter.response.send_message(f"Произошла ошибка: {e}", ephemeral=True)

    async def send_embed_via_webhook(self, webhook_url, embed):
        """Отправляет эмбед через вебхук."""
        embed_data = {
            "embeds": [embed.to_dict()]  # Преобразуем эмбед в словарь
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=embed_data) as response:
                if response.status != 204:
                    raise Exception(f"Ошибка при отправке вебхука: {response.status} {await response.text()}")


    @commands.slash_command(description="Отправить эмбед через вебхук")
    async def send_webhook_embed(self, inter: disnake.CommandInteraction, webhook_url: str, json_data: str):
        try:
            # Парсим JSON-строку
            data = json.loads(json_data)

            # Создаем эмбед
            embed = disnake.Embed(
                title=self.replace_variables(data.get('title'), inter.user, inter.guild, inter.guild.get_member(inter.user.id)),
                description=self.replace_variables(data.get('description'), inter.user, inter.guild, inter.guild.get_member(inter.user.id)),
                url=self.replace_variables(data.get('url'), inter.user, inter.guild, inter.guild.get_member(inter.user.id)),
                color=self.get_color(data.get('color')),
                timestamp=self.parse_timestamp(data.get('timestamp'))
            )

            # Добавляем footer, если он есть
            if 'footer' in data:
                footer_data = data['footer']
                if 'text' not in footer_data:
                    await inter.response.send_message("Ошибка: У футера отсутствует текст.", ephemeral=True)
                    return
                footer_icon_url = self.replace_variables(footer_data.get('icon_url', self.bot.user.avatar.url), inter.user, inter.guild, inter.guild.get_member(inter.user.id))
                embed.set_footer(
                    text=self.replace_variables(footer_data['text'], inter.user, inter.guild, inter.guild.get_member(inter.user.id)),
                    icon_url=footer_icon_url if self.is_valid_url(footer_icon_url) else None
                )

            # Добавляем thumbnail, если он есть
            if 'thumbnail' in data:
                thumbnail_url = self.replace_variables(data['thumbnail']['url'], inter.user, inter.guild, inter.guild.get_member(inter.user.id))
                if self.is_valid_url(thumbnail_url):
                    embed.set_thumbnail(url=thumbnail_url)

            # Добавляем image, если он есть
            if 'image' in data:
                image_url = self.replace_variables(data['image']['url'], inter.user, inter.guild, inter.guild.get_member(inter.user.id))
                if self.is_valid_url(image_url):
                    embed.set_image(url=image_url)

            # Добавляем author, если он есть
            if 'author' in data:
                author_data = data['author']
                if 'name' not in author_data:
                    await inter.response.send_message("Ошибка: У автора отсутствует имя.", ephemeral=True)
                    return
                author_icon_url = self.replace_variables(author_data.get('icon_url', inter.user.avatar.url if inter.user.avatar else None), inter.user, inter.guild, inter.guild.get_member(inter.user.id))
                embed.set_author(
                    name=self.replace_variables(author_data['name'], inter.user, inter.guild, inter.guild.get_member(inter.user.id)),
                    url=self.replace_variables(author_data.get('url'), inter.user, inter.guild, inter.guild.get_member(inter.user.id)),
                    icon_url=author_icon_url if self.is_valid_url(author_icon_url) else None
                )

            # Добавляем поля, если они есть
            if 'fields' in data:
                for field in data['fields']:
                    embed.add_field(
                        name=self.replace_variables(field['name'], inter.user, inter.guild, inter.guild.get_member(inter.user.id)),
                        value=self.replace_variables(field['value'], inter.user, inter.guild, inter.guild.get_member(inter.user.id)),
                        inline=field.get('inline', False)
                    )

            # Отправляем эмбед через вебхук
            await self.send_embed_via_webhook(webhook_url, embed)

            # Уведомляем пользователя об успешной отправке
            await inter.response.send_message("Эмбед успешно отправлен через вебхук.", ephemeral=True)

        except json.JSONDecodeError:
            await inter.response.send_message("Ошибка: Неверный формат JSON.", ephemeral=True)
        except Exception as e:
            await inter.response.send_message(f"Произошла ошибка: {e}", ephemeral=True)

    def parse_timestamp(self, timestamp):
        """Преобразует строку или целое число в объект datetime или возвращает None."""
        if isinstance(timestamp, int):
            return datetime.fromtimestamp(timestamp / 1000)  # Делим на 1000, если это миллисекунды
        elif isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp[:-1])  # Убираем 'Z' в конце
            except ValueError:
                return None
        return None

    def get_color(self, color):
        """Преобразует строку цвета в disnake.Colour или возвращает стандартный цвет."""
        if isinstance(color, str):
            if color.startswith('#'):
                color = color[1:]
            try:
                return int(color, 16)  # Преобразуем шестнадцатеричную строку в целое число
            except ValueError:
                return disnake.Colour.default()  # Возвращаем стандартный цвет, если произошла ошибка
        elif isinstance(color, int):
            return color  # Если это уже целое число, возвращаем его
        return disnake.Colour.default()  # Возвращаем стандартный цвет, если ничего не подошло

    def replace_variables(self, text, author, guild, member):
        """Заменяет переменные в тексте на соответствующие значения."""
        if text is None:
            return None

        # Заменяем стандартные переменные
        text = text.replace("{author}", str(author))
        text = text.replace("{bot}", str(self.bot.user))
        text = text.replace("{guild}", str(guild))

        # Заменяем переменные для автора
        author_avatar_url = author.avatar.url if author.avatar else None
        text = text.replace("{author_avatar}", author_avatar_url if author_avatar_url else "")

        # Заменяем переменные для участника по ID
        if "{member:" in text:
            while "{member:" in text:
                start_index = text.index("{member:") + len("{member:")
                end_index = text.index("}", start_index)
                member_id = int(text[start_index:end_index])  # Получаем ID участника
                member = guild.get_member(member_id)  # Получаем объект участника

                # Заменяем переменную на имя участника или на "Unknown" если не найден
                member_name = str(member) if member else "Unknown"
                text = text.replace(f"{{member:{member_id}}}", member_name)

        # Заменяем переменные для аватара участника по ID
        if "{member_avatar:" in text:
            while "{member_avatar:" in text:
                start_index = text.index("{member_avatar:") + len("{member_avatar:")
                end_index = text.index("}", start_index)
                member_id = int(text[start_index:end_index])  # Получаем ID участника
                member = guild.get_member(member_id)  # Получаем объект участника

                # Заменяем переменную на URL аватара участника или на None если не найден
                member_avatar_url = member.avatar.url if member else None
                text = text.replace(f"{{member_avatar:{member_id}}}", member_avatar_url if member_avatar_url else "")

        return text

def setup(bot):
    bot.add_cog(Embed(bot))

