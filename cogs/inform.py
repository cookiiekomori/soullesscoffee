from imports import *

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

settings = load_config()

class Information(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Модуль {self.__class__.__name__} подключен.")

    @commands.slash_command(description="Информационные команды")
    async def info(self, interaction: disnake.ApplicationCommandInteraction):
        pass 

# Информация о боте -----------------------------------------------------------------------------------------------------------
    @info.sub_command(description="Информация о боте")
    async def bot(self, interaction: disnake.ApplicationCommandInteraction):
        creator = "<@528724400850206720>"
        server_count = len(self.bot.guilds)
        member_count = sum(guild.member_count for guild in self.bot.guilds)
        ping = round(self.bot.latency * 1000)
        version = settings['version']
        python_version = sys.version.split()[0]
        disnake_version = disnake.__version__
        support_server_link = "[>тык<](https://discord.gg/ZSUpv25GRz)"
        
        command_count = len(self.bot.commands) + len(self.bot.application_commands)

        embed = disnake.Embed(title="Информация о боте", color=disnake.Color.from_rgb(43, 45, 49))
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.add_field(name="Создатель", value=creator, inline=False)
        embed.add_field(name="Серверов", value=f"```{server_count}```", inline=True)
        embed.add_field(name="Участников", value=f"```{member_count}```", inline=True)
        embed.add_field(name="Количество команд", value=f"```{command_count}```", inline=True)
        embed.add_field(name="Версия Python", value=f"```{python_version}```", inline=True)
        embed.add_field(name="Версия Disnake", value=f"```{disnake_version}```", inline=True)
        embed.add_field(name="Версия бота", value=f"```{version}```", inline=True)
        embed.add_field(name="Ссылка на сервер поддержки", value=support_server_link, inline=False)
        embed.set_footer(text=f"Пинг {ping} ms")

        await interaction.send(embed=embed)

# Информация о пользователе -----------------------------------------------------------------------------------------------------------
    @info.sub_command(description="Информация о пользователе")
    async def user(self, interaction: disnake.ApplicationCommandInteraction, member: disnake.Member = None):
        if member is None:
            member = interaction.user

        user_id = member.id
        username = str(member)
        joined_at = member.joined_at.strftime("%Y-%m-%d %H:%M:%S") 
        roles = ", ".join([role.name for role in member.roles[1:]]) 
        avatar_url = member.avatar.url if member.avatar else None 
        status_mapping = {
            disnake.Status.online: "Онлайн",
            disnake.Status.idle: "Неактивен",
            disnake.Status.dnd: "Не беспокоить",
            disnake.Status.offline: "Оффлайн",
            disnake.Status.streaming: "Стримит" 
        }
        status = status_mapping.get(member.status, "Неизвестен")
        created_at = member.created_at.strftime("%Y-%m-%d %H:%M:%S")

        activity = "Нет активности"
        activity_label = "Активность"

        if member.activity:
            if member.activity.type == disnake.ActivityType.playing:
                activity = f"Играет в {member.activity.name}"
            elif member.activity.type == disnake.ActivityType.streaming:
                activity = f"Стримит {member.activity.title} на {member.activity.platform}"
            elif member.activity.type == disnake.ActivityType.listening:
                activity = f"Слушает {member.activity.title}"
            elif member.activity.type == disnake.ActivityType.watching:
                activity = f"Смотрит {member.activity.title}"
            elif member.activity.type == disnake.ActivityType.custom:
                activity = f"{member.activity.name}"
                activity_label = "Статус"
            else:
                activity = "Неизвестная активность"

        is_bot = "Ботяра" if member.bot else "Не бот"

        embed = disnake.Embed(title="Информация о пользователе", color=disnake.Color.from_rgb(43, 45, 49))
        if avatar_url:
            embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="Имя", value=f"```{username}```", inline=True)
        embed.add_field(name="Бот?", value=f"```{is_bot}```", inline=True)
        embed.add_field(name=activity_label, value=f"```{activity}```", inline=False)
        embed.add_field(name="Роли", value=f"```{roles if roles else 'Нет ролей'}```", inline=False)
        embed.add_field(name="Дата создания аккаунта", value=f"```{created_at}```", inline=True)
        embed.add_field(name="Дата присоединения", value=f"```{joined_at}```", inline=True)
        embed.set_footer(text=f"ID - {user_id}")

        await interaction.send(embed=embed)

# Информация о гильдии -----------------------------------------------------------------------------------------------------------
    @info.sub_command(description="Информация о гильдии")
    async def guild(self, interaction: disnake.ApplicationCommandInteraction):
        guild = interaction.guild  # Получаем объект гильдии из взаимодействия

        guild_id = guild.id
        guild_name = guild.name
        member_count = guild.member_count
        role_count = len(guild.roles) - 1  # Исключаем роль @everyone
        created_at = guild.created_at.strftime("%Y-%m-%d %H:%M:%S")
        owner = guild.owner  # Владелец гильдии
        preferred_locale = guild.preferred_locale  # Локаль гильдии
        icon_url = guild.icon.url if guild.icon else None  # URL иконки гильдии

        # Сбор статистики по каналам
        channel_count = len(guild.channels)  # Общее количество каналов
        text_channel_count = len(guild.text_channels)  # Количество текстовых каналов
        voice_channel_count = len(guild.voice_channels)  # Количество голосовых каналов
        category_count = len(guild.categories)  # Количество категорий

        embed = disnake.Embed(title="Информация о гильдии", color=disnake.Color.from_rgb(43, 45, 49))
        if icon_url:
            embed.set_thumbnail(url=icon_url)
        embed.add_field(name="Имя гильдии", value=f"```{guild_name}```", inline=False)

        embed.add_field(name="Кол-во юзеров", value=f"```{member_count}```", inline=True)
        embed.add_field(name="Кол-во ролей", value=f"```{role_count}```", inline=True)
        embed.add_field(name="Кол-во категорий", value=f"```{category_count}```", inline=True)
        embed.add_field(name="Общее количество каналов", value=f"```{channel_count}```", inline=False)
        embed.add_field(name="Кол-во каналов", value=f"```{text_channel_count}```", inline=True)
        embed.add_field(name="Кол-во войсов", value=f"```{voice_channel_count}```", inline=True)
        embed.add_field(name="Владелец", value=f"```{owner}```", inline=False)
        embed.add_field(name="Дата создания", value=f"```{created_at}```", inline=True)
        embed.add_field(name="Локализация", value=f"```{preferred_locale}```", inline=True)
        embed.set_footer(text=f"ID гильдии - {guild_id}")

        await interaction.send(embed=embed)



# Список команд -----------------------------------------------------------------------------------------------------------------------
    @info.sub_command(description="Список всех команд")
    async def commands(self, interaction: disnake.ApplicationCommandInteraction):

        owner_only_commands = ['load', 'reload', 'unload', 'restart', 'update', 'send_webhook_embed']  # Список команд, которые требуют прав владельца

        command_names = [cmd.name for cmd in self.bot.commands if cmd.name not in owner_only_commands]
        slash_command_names = [cmd.name for cmd in self.bot.application_commands if cmd.name not in owner_only_commands]
        command_list = "\n".join(f"{settings['prefix']}{name}" for name in command_names) if command_names else "Нет обычных команд."
        slash_command_list = "\n".join(f"/{name}" for name in slash_command_names) if slash_command_names else "Нет слэш-команд."
        
        # Используем цвет из HEX
        embed = disnake.Embed(title="Список всех команд", color=disnake.Color.from_rgb(43, 45, 49))
        embed.add_field(name="Префикс команды", value=f"```\n{command_list}```", inline=True)
        embed.add_field(name="Слэш-команды", value=f"```\n{slash_command_list}```", inline=True)
        
        await interaction.send(embed=embed)


def setup(bot):
    bot.add_cog(Information(bot))
