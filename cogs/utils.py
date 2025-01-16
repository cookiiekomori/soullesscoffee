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
        embed = disnake.Embed(
            title=f"Использование команды: `/update`",
            color=disnake.Color.red()
        )
        embed.add_field(name="Пользователь", value=interaction.author.mention, inline=True)
        embed.add_field(name="Канал", value=interaction.channel.mention, inline=True)
        embed.set_image(url="https://i.imgur.com/Y0MGCWI.png")

        await self.send_webhook(settings['webhook_url']['command_log'], embed)
        pass

    def get_cogs(self):
        return [filename[:-3] for filename in os.listdir("cogs") if filename.endswith(".py")]

# Обновление мажорной версии -----------------------------------------------------------------------------------------------
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

# Рестарт бота -------------------------------------------------------------------------------------------------------------
    @update.sub_command(name='commit', description='Залить обновление на GitHub')
    async def commit(self, interaction: disnake.ApplicationCommandInteraction):
        await interaction.response.send_message("Начинаю обновление...")
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


            await interaction.followup.send(f"Обновление завершено успешно!\nВерсия обновлена до: {config['version']}")
            await interaction.followup.send("Начата перезагрузка бота, подождите 10 секунд до начала использования команд")
            os.execv(sys.executable, ['python'] + sys.argv)

        except subprocess.CalledProcessError as e:
            await interaction.followup.send(f"Произошла ошибка при обновлении: {e}")

# Перезапуск бота -------------------------------------------------------------------------------------------------------------
    @update.sub_command(name='restart', description='Перезагрузить бота')
    async def restart(self, interaction: disnake.ApplicationCommandInteraction):
        await interaction.response.send_message("Перезагрузка бота...")
        os.execv(sys.executable, ['python'] + sys.argv)

# Purge command ----------------------------------------------------------------------------------------------------------------
    def is_owner_or_cooldown():
        def predicate(interaction: disnake.CommandInteraction):
            command = interaction.data['name']
            cmd = interaction.bot.get_slash_command(command)
            return interaction.author.id == interaction.bot.owner_id or not cmd.is_on_cooldown(interaction)
        return commands.check(predicate)

    @commands.slash_command(description="Очищает указанное количество сообщений из канала.")
    @commands.has_permissions(manage_messages=True)
    @is_owner_or_cooldown()
    async def purge(self, interaction: disnake.CommandInteraction, amount: int = None):
        if amount is None:
            await interaction.response.send_message("Пожалуйста, укажите количество сообщений для удаления.", ephemeral=True)
            return

        if interaction.author.id != interaction.bot.owner_id:
            if amount < 1 or amount > 20:
                await interaction.response.send_message("Количество сообщений должно быть от 1 до 20.", ephemeral=True)
                return

        deleted = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"Удалено {len(deleted)} сообщений.", ephemeral=True)

        embed = disnake.Embed(
            title=f"Использование команды: `/purge`",
            color=disnake.Color.red()
        )
        embed.add_field(name="Пользователь", value=interaction.author.mention, inline=True)
        embed.add_field(name="Канал", value=interaction.channel.mention, inline=True)
        embed.add_field(name="Количество удаленных сообщений", value=len(deleted), inline=False)
        embed.set_image(url="https://i.imgur.com/Y0MGCWI.png")

        await self.send_webhook(settings['webhook_url']['command_log'], embed)

    @purge.error
    async def purge_error(self, interaction: disnake.CommandInteraction, error):
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.response.send_message(f"Вы можете использовать эту команду снова через {error.retry_after:.2f} секунд.", ephemeral=True)


    async def send_webhook(self, webhook_url, embed=None, content=None):
        try:
            async with aiohttp.ClientSession() as session:
                webhook = disnake.Webhook.from_url(webhook_url, session=session)
                if embed:
                    await webhook.send(embed=embed)
                elif content:
                    await webhook.send(content)
        except Exception as e:
            print(f"Ошибка при отправке вебхука: {e}")
# --------------------------------------------------------------------------------------------------------------------------------------


def setup(bot):
    bot.add_cog(Utilites(bot))
