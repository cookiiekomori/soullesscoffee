import disnake
import json
from disnake.ext import commands
from datetime import datetime

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

    @commands.slash_command(description="Создать эмбед из JSON")
    async def create_embed(self, inter: disnake.CommandInteraction, json_data: str):
        owner_id = self.bot.owner_id
        allowed_role_ids = *self.admin_role_id, self.developer_role_id
        if ctx.author.id != owner_id and not any(role.id in allowed_role_ids for role in ctx.author.roles):
            await ctx.send("Недостаточно прав для использования этой команды.")
            return
        try:
            # Парсим JSON-строку
            data = json.loads(json_data)

            # Создаем эмбед
            embed = disnake.Embed(
                title=data['embed']['title'],
                description=data['embed']['description'],
                url=data['embed'].get('url'),
                color=data['embed']['color'],
                timestamp=self.parse_timestamp(data['embed'].get('timestamp'))  # Преобразуем строку в datetime
            )

            # Добавляем footer, если он есть
            if 'footer' in data['embed']:
                embed.set_footer(
                    text=data['embed']['footer']['text'],
                    icon_url=data['embed']['footer']['icon_url']
                )

            # Добавляем thumbnail, если он есть
            if 'thumbnail' in data['embed']:
                embed.set_thumbnail(url=data['embed']['thumbnail']['url'])

            # Добавляем image, если он есть
            if 'image' in data['embed']:
                embed.set_image(url=data['embed']['image']['url'])

            # Добавляем author, если он есть
            if 'author' in data['embed']:
                embed.set_author(
                    name=data['embed']['author']['name'],
                    url=data['embed']['author'].get('url'),
                    icon_url=data['embed']['author']['icon_url']
                )

            # Добавляем поля, если они есть
            if 'fields' in data['embed']:
                for field in data['embed']['fields']:
                    embed.add_field(
                        name=field['name'],
                        value=field['value'],
                        inline=field.get('inline', False)
                    )

            # Отправляем сообщение с эмбед
            await inter.response.send_message(content=data.get('content', ''), embed=embed)

        except json.JSONDecodeError:
            await inter.response.send_message("Ошибка: Неверный формат JSON.", ephemeral=True)
        except Exception as e:
            await inter.response.send_message(f"Произошла ошибка: {e}", ephemeral=True)

    def parse_timestamp(self, timestamp_str):
        """Преобразует строку в объект datetime или возвращает None."""
        if timestamp_str:
            try:
                return datetime.fromisoformat(timestamp_str[:-1])  # Убираем 'Z' в конце
            except ValueError:
                return None
        return None

def setup(bot):
    bot.add_cog(Embed(bot))
    print(f"Подключение модуля Embed...")