from imports import *

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

settings = load_config()

class Utilites(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Модуль {self.__class__.__name__} подключен.")

    @commands.slash_command(description="Команда для обновления версии бота")
    @commands.is_owner()
    async def update(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    def get_cogs(self):
        return [filename[:-3] for filename in os.listdir("cogs") if filename.endswith(".py")]

    @update.sub_command(description="Увеличить мажорную версию на 1")
    async def congratulation(self, interaction: disnake.ApplicationCommandInteraction):
        config = load_config()
        major, minor, patch = map(int, config['version'].split('.'))
        major += 1 
        minor = len(self.get_cogs())
        patch = 0 

        config['version'] = f"{major}.{minor}.{patch}"
        save_config(config)

        await interaction.response.send_message(f"Версия обновлена до: {config['version']}")

    @update.sub_command(name='restart', description='Перезагрузить бота')
    async def restart(self, interaction: disnake.ApplicationCommandInteraction):
        await interaction.response.send_message("Перезагрузка бота...")
        os.execv(sys.executable, ['python'] + sys.argv)


    @update.sub_command(name='commit', description='Залить обновление на GitHub')
    async def commit(self, ctx):
        await ctx.send("Начинаю обновление...")
        config = load_config()
        major, minor, patch = map(int, config['version'].split('.'))
        minor = len(self.get_cogs()) 
        patch += 1 
        config['version'] = f"{major}.{minor}.{patch}"
        save_config(config)

        try:
            os.chdir('C:\\Users\\cooki\\Desktop\\Homework\\soullesscoffee')

            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', 'update'], check=True)
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)

            await ctx.send(f"Обновление завершено успешно!\nВерсия обновлена до: {config['version']}")
        except subprocess.CalledProcessError as e:
            await ctx.send(f"Произошла ошибка при обновлении: {e}")

def setup(bot):
    bot.add_cog(Utilites(bot))
