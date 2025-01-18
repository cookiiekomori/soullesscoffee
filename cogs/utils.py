from imports import *

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

settings = load_config()

class Utilites(commands.Cog):
    """Утилиты"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Модуль {self.__class__.__name__} подключен.")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Получаем информацию о боте и авторе
        bot_user = self.bot.user
        author = guild.owner  # Владелец сервера
        member = guild.me  # Бот как участник сервера

        # Создаем эмбед
        embed = disnake.Embed(title="Настройка бота под Ваш сервер", 
            description="Для корректной работы бота на сервере, ему необходима настройка.\nНиже представлен список команд\n\n",
            color=disnake.Color.from_rgb(43, 45, 49))
        embed.add_field(name="Гендерные роли\nПредназначены для работы с /fun.. командами", value=f"```/configuration gender male_id female_id```", inline=False)
        embed.add_field(name="Модерационные роли", value=f"```Тут какой-то текст```", inline=False)
        embed.add_field(name="Тут какой-то текст", value=f"```Тут какой-то текст```", inline=False)

        # Попытка отправить в ЛС владельцу сервера
        try:
            await author.send(embed=embed)
        except disnake.Forbidden:
            # Если не удалось отправить в ЛС, создаем закрытый канал
            overwrites = {
                guild.default_role: disnake.PermissionOverwrite(read_messages=False),  # Запретить всем
                author: disnake.PermissionOverwrite(read_messages=True)  # Разрешить владельцу
            }
            private_channel = await guild.create_text_channel(
                name=f"private-{author.name}",
                overwrites=overwrites,
                reason="Создан для отправки сообщения владельцу сервера"
            )
            await private_channel.send(embed=embed)
            await private_channel.send(f"{author.mention}, это ваш закрытый канал для общения с ботом.")

    @commands.slash_command(guild_ids=[854309914788626442], description="Команда для обновления версии бота")
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
    @update.sub_command(guild_ids=[854309914788626442], description="Увеличить мажорную версию на 1")
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
    @update.sub_command(guild_ids=[854309914788626442], name='commit', description='Залить обновление на GitHub')
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
    @update.sub_command(guild_ids=[854309914788626442], name='restart', description='Перезагрузить бота')
    async def restart(self, interaction: disnake.ApplicationCommandInteraction):
        await interaction.response.send_message("Перезагрузка бота...")
        os.execv(sys.executable, ['python'] + sys.argv)

# Purge command ----------------------------------------------------------------------------------------------------------------
    @commands.slash_command(description="Очищает указанное количество сообщений из канала.")
    @commands.cooldown(1, 20, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def purge(self, interaction: disnake.CommandInteraction, amount: int = None):
        if amount is None:
            await interaction.response.send_message("Пожалуйста, укажите количество сообщений для удаления.", ephemeral=True)
            return

        if interaction.author.id != interaction.bot.owner_id:
            if amount < 1 or amount > 20:
                await interaction.response.send_message("Количество сообщений должно быть от 1 до 20.", ephemeral=True)
                return
                
        await self.clear_messages(interaction, amount)

    async def clear_messages(self, interaction: disnake.CommandInteraction, amount: int):
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

    @commands.slash_command(description="Команда для конфигурации бота")
    @commands.has_permissions(administrator=True)
    async def configuration(self, interaction: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(
            title=f"Использование команды: `/configuration`",
            color=disnake.Color.red()
        )
        embed.add_field(name="Пользователь", value=interaction.author.mention, inline=True)
        embed.add_field(name="Канал", value=interaction.channel.mention, inline=True)
        embed.set_image(url="https://i.imgur.com/Y0MGCWI.png")

        await self.send_webhook(settings['webhook_url']['command_log'], embed)
        pass

    @configuration.sub_command(name='gender', description='Вписать id мужской роли и женской роли')
    async def gender(self, ctx, male_role_id, female_role_id):
        df = pd.read_csv('Bases\\guild_configurations.csv')
        in_data = df[(df["Guild_id"] == int(ctx.guild.id)) & (df["Male_role_id"] == int(male_role_id)) & (df["Female_role_id"] == int(female_role_id))]
        if in_data.empty:
            df.loc[len(df)] = [ctx.guild.name, int(ctx.guild.id), int(male_role_id), int(female_role_id)]
            await ctx.send("Успешно! Гендерные роли были добавлены!", ephemeral=True)
        else:
            await ctx.send("Ошибка! Роли уже были добавлены", ephemeral=True)
        df.to_csv('Bases\\guild_configurations.csv', index=False)


def setup(bot):
    bot.add_cog(Utilites(bot))
