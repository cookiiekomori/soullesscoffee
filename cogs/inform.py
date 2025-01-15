import disnake
from disnake.ext import commands
import json
import sys
import os

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

    @commands.slash_command(description="Команда для обновления версии бота")
    @commands.is_owner()
    async def update(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @commands.slash_command(description="Информационные команды")
    async def info(self, interaction: disnake.ApplicationCommandInteraction):
        pass 

    @info.sub_command(description="Информация о боте")
    async def bot(self, interaction: disnake.ApplicationCommandInteraction):
        creator = "<@528724400850206720>"
        server_count = len(self.bot.guilds)
        member_count = sum(guild.member_count for guild in self.bot.guilds)
        ping = round(self.bot.latency * 1000)
        version = settings['version']
        python_version = sys.version.split()[0]  # Получаем версию Python
        disnake_version = disnake.__version__  # Получаем версию Disnake
        support_server_link = "[>тык<](https://discord.gg/ZSUpv25GRz)"
        
        command_count = len(self.bot.commands) + len(self.bot.application_commands)

        # Используем цвет из HEX
        embed = disnake.Embed(title="Информация о боте", color=disnake.Color.from_rgb(43, 45, 49))
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.add_field(name="Создатель", value=creator, inline=False)
        embed.add_field(name="Серверов", value=f"```{server_count}```", inline=True)
        embed.add_field(name="Участников", value=f"```{member_count}```", inline=True)
        embed.add_field(name="Количество команд", value=f"```{command_count}```", inline=False)
        embed.add_field(name="Пинг", value=f"{ping} ms", inline=False)
        embed.add_field(name="Версия Python", value=python_version, inline=True)
        embed.add_field(name="Версия Disnake", value=disnake_version, inline=True)
        embed.add_field(name="Ссылка на сервер поддержки", value=support_server_link, inline=False)
        embed.set_footer(text=f"Версия бота: {version}")

        await interaction.send(embed=embed)

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

    def get_cogs(self):
        return [filename[:-3] for filename in os.listdir("cogs") if filename.endswith(".py")]

    @update.sub_command(description="Увеличить патч-версию на 1")
    async def commit(self, interaction: disnake.ApplicationCommandInteraction):
        config = load_config()
        major, minor, patch = map(int, config['version'].split('.'))
        minor = len(self.get_cogs())  # Обновляем минорную версию на количество когов
        patch += 1  # Увеличиваем патч-версию на 1
        config['version'] = f"{major}.{minor}.{patch}"
        save_config(config)

        await interaction.response.send_message(f"Версия обновлена до: {config['version']}")

    @update.sub_command(description="Увеличить мажорную версию на 1")
    async def congratulation(self, interaction: disnake.ApplicationCommandInteraction):
        config = load_config()
        major, minor, patch = map(int, config['version'].split('.'))
        major += 1  # Увеличиваем мажорную версию на 1
        minor = len(self.get_cogs())  # Обновляем минорную версию на количество когов
        patch = 0  # Сбрасываем патч-версию

        config['version'] = f"{major}.{minor}.{patch}"
        save_config(config)

        await interaction.response.send_message(f"Версия обновлена до: {config['version']}")

def setup(bot):
    bot.add_cog(Information(bot))
