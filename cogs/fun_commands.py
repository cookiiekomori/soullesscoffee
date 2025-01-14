import disnake
from disnake.ext import commands
import json
import random

# Функция для загрузки конфигурации
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Модуль {self.__class__.__name__} подключен.")

    @commands.slash_command(description="Ударить по попе")
    async def slap(self, interaction: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        # Если пользователь не указан, используем автора команды
        if user is None:
            user = interaction.user

        # Получаем роли пользователя
        roles = interaction.user.roles

        # ID ролей для определения пола
        female_role_id = self.config["roles"]["female"]["role_id"]
        male_role_id = self.config["roles"]["male"]["role_id"]

        # Проверяем наличие женской или мужской роли
        has_female_role = any(role.id == female_role_id for role in roles)
        has_male_role = any(role.id == male_role_id for role in roles)

        if not has_female_role and not has_male_role:
            await interaction.send("Ты по-моему что-то перепутал, ты либо не на том сервере, либо определи себя, мужчина ты или женщина, отказано в выполнении команды.")
            return

        # Определяем, как описать действие в зависимости от роли
        if has_female_role:
            action_description = "ударила"
        else:
            action_description = "ударил"

        # Проверяем, ударил ли автор себя
        if user == interaction.user:
            description = f"{interaction.user.mention} {action_description} себя по попе!"
            # Список гифок для удара по себе
            gif_list = [
                "https://media.tenor.com/AEWh7M4iBEYAAAAM/spanking-spank.gif",
                "https://media.tenor.com/MWOs_f48n2cAAAAM/slap-my-ass-godku.gif",
                "https://media.tenor.com/L94kvBQ5BH8AAAAM/pingu-slap.gif"
            ]
        else:
            description = f"{interaction.user.mention} {action_description} по попе {user.mention}!"
            # Список гифок для удара по другому пользователю
            gif_list = [
                "https://media.tenor.com/XW_ymVr5I6sAAAAM/slap-butt.gif", 
                "https://media.tenor.com/AiLrNJMakwIAAAAM/mochi-bunny.gif",
                "https://media.tenor.com/v20N16whtvoAAAAM/butt-slap-booty-slap.gif"
            ]

        # Создаем эмбед
        embed = disnake.Embed(
            description=description,
            color=disnake.Color.default()  # Используем стандартный цвет
        )
        
        # Выбираем случайную гифку из списка
        random_gif = random.choice(gif_list)
        embed.set_image(url=random_gif)

        # Устанавливаем футер
        embed.set_footer(text="Отшлепан как следует")

        # Отправляем эмбед
        await interaction.send(embed=embed)

# Функция для добавления cog в бота
def setup(bot):
    bot.add_cog(FunCommands(bot))
