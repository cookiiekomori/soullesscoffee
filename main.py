import disnake
import os
import asyncio
from disnake.ext import commands, tasks
import json
import aiohttp
import nacl
import sys
import subprocess

# Загрузка конфигурации
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Сохранение конфигурации
def save_config(config):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

# Загрузка конфигурации
settings = load_config()  # Здесь вы загружаете данные из JSON в переменную settings

# Создание бота
intents = disnake.Intents().all()
intents.message_content = True
intents.voice_states = True  # Включаем интенты для работы с голосовыми состояниями
intents.guilds = True  # Включаем интенты для работы с серверами
bot = commands.Bot(command_prefix=settings['prefix'], intents=intents)

print("Идет процесс запуска, ожидайте...")

@tasks.loop(seconds=15)
async def update_voice_channel_name():
    total_members = 0

    # Проходим по всем голосовым каналам на всех серверах
    for guild in bot.guilds:
        for channel in guild.voice_channels:
            total_members += len(channel.members)

    # Получаем целевой голосовой канал по ID
    target_voice_channel = bot.get_channel(settings['TARGET_VOICE_CHANNEL_ID'])
    if target_voice_channel:
        new_name = f'🍥 » В войсе {total_members}'
        
        # Обработка ошибок при редактировании канала
        try:
            await target_voice_channel.edit(name=new_name)
        except disnake.errors.DiscordServerError as e:
            print(f"Ошибка при редактировании канала: {e}. Повторная попытка через 5 секунд.")
            await asyncio.sleep(60)  # Ждем 5 секунд перед повторной попыткой
            await update_voice_channel_name()  # Повторяем попытку

@bot.event
async def on_ready():
    print(f"-------------------------\nУспешно запущен бот, {bot.user.name}")
    bot.loop.create_task(status_task(bot))
    update_voice_channel_name.start() 
@bot.event
async def on_command(ctx):
    print(f"Команда '{ctx.command}' была вызвана пользователем {ctx.author} в канале {ctx.channel}.")

@bot.event
async def on_command_error(ctx, error):
    print(f"Ошибка при выполнении команды '{ctx.command}': {error}")

async def status_task(bot):
    while True:
        try:
            await bot.change_presence(activity=disnake.Streaming(name="куки", url="https://www.twitch.tv/videos/225796573?t=00h00m30s"))
            await asyncio.sleep(15)

            await bot.change_presence(activity=disnake.Streaming(name=f"use {settings['prefix']}help for help", url="https://www.twitch.tv/videos/225796573?t=00h00m30s"))
            await asyncio.sleep(15)

            guilds = bot.guilds
            total_members = sum(guild.member_count for guild in guilds)
            await bot.change_presence(activity=disnake.Streaming(name=f"{total_members} users on {len(guilds)} guilds", url="https://www.twitch.tv/videos/225796573?t=00h00m30s"))
            await asyncio.sleep(15)

        except disnake.HTTPException as e:
            print(f"Ошибка при изменении статуса 'стримит': {e}")
            await asyncio.sleep(5)


# Загрузка модулей
for filename in os.listdir("cogs"):
    if filename.endswith(".py"):
        bot.load_extension("cogs." + filename[:-3])

# Функция для получения списка когов
def get_cogs():
    return [filename[:-3] for filename in os.listdir("cogs") if filename.endswith(".py")]

# Статический список когов с дескрипшенами
static_cogs = [
    disnake.OptionChoice(name="ctx_commands", value="ctx_commands"),
    disnake.OptionChoice(name="embed", value="embed"),
    disnake.OptionChoice(name="logging", value="logging"),
]  # Замените на ваши названия когов

@bot.slash_command(description="Выводит список доступных модулей")
@commands.is_owner()
async def list_cogs(inter: disnake.CommandInteraction):
    cog_list = "\n".join(get_cogs())
    await inter.response.send_message(f"Список модулей:```\n{cog_list}\n```", ephemeral=True)

@bot.slash_command(description="Загрузить модуль бота")
@commands.is_owner()
async def load(inter: disnake.CommandInteraction, 
               module: str = disnake.Option(name="module", 
                                            description="Выберите модуль для загрузки", 
                                            choices=static_cogs)):
    try:
        bot.load_extension(f"cogs.{module}")
        await inter.response.send_message(f"Загружен модуль `{module}`", ephemeral=True)
        print(f"Загружен модуль {module}")
    except Exception as e:
        await inter.response.send_message(f"Ошибка при загрузке модуля `{module}`: {e}", ephemeral=True)

@bot.slash_command(description="Выгрузить модуль бота")
@commands.is_owner()
async def unload(inter: disnake.CommandInteraction, 
                 module: str = disnake.Option(name="module", 
                                              description="Выберите модуль для выгрузки", 
                                              choices=static_cogs)):
    try:
        bot.unload_extension(f"cogs.{module}")
        await inter.response.send_message(f"Выгружен модуль `{module}`", ephemeral=True)
        print(f"Выгружен модуль {module}")
    except Exception as e:
        await inter.response.send_message(f"Ошибка при выгрузке модуля `{module}`: {e}", ephemeral=True)

@bot.slash_command(description="Перезагрузить модуль бота")
@commands.is_owner()
async def reload(inter: disnake.CommandInteraction, 
                  module: str = disnake.Option(name="module", 
                                               description="Выберите модуль для перезагрузки", 
                                               choices=static_cogs)):
    try:
        bot.reload_extension(f"cogs.{module}")
        await inter.response.send_message(f"Перезагружен модуль `{module}`", ephemeral=True)
        print(f"Перезагружен модуль {module}")
    except Exception as e:
        await inter.response.send_message(f"Ошибка при перезагрузке модуля `{module}`: {e}", ephemeral=True)




def is_owner_or_cooldown():
    def predicate(ctx):
        return ctx.author.id == ctx.bot.owner_id or not ctx.command.is_on_cooldown(ctx)
    return commands.check(predicate)

@bot.slash_command(description="Очищает указанное количество сообщений из канала.")
@commands.has_permissions(manage_messages=True)  # Проверка на наличие разрешения
@is_owner_or_cooldown()  # Проверка на владельца или отсутствие кулдауна
async def purge(inter: disnake.CommandInteraction, amount: int = None):
    if amount is None:
        await inter.response.send_message("Пожалуйста, укажите количество сообщений для удаления.", ephemeral=True)
        return

    # Снятие ограничения на количество удаляемых сообщений для владельца
    if inter.author.id != inter.bot.owner_id:
        if amount < 1 or amount > 20:
            await inter.response.send_message("Количество сообщений должно быть от 1 до 20.", ephemeral=True)
            return

    deleted = await inter.channel.purge(limit=amount)
    await inter.response.send_message(f"Удалено {len(deleted)} сообщений.", ephemeral=True)  # Скрытое сообщение

    # Логирование использования команды в вебхук с эмбед
    log_message = (
        f"Команда 'purge' использована пользователем **{inter.author.name}**\n\n"
        f"Канал: **{inter.channel.mention}** (ID: {inter.channel.id})\n\n"
        f"Сервер: **{inter.guild.name}** (ID: {inter.guild.id})\n"
    )
    
    embed = disnake.Embed(
        title="Лог команды 'purge'",
        description=log_message,
        color=disnake.Color.red()  # Вы можете выбрать любой цвет
    )
    embed.set_footer(text=f"Удалено сообщений: {len(deleted)}")  # Добавляем количество удаленных сообщений в footer
    await send_webhook(settings['webhook_url']['command_log'], embed)

# Установка кулдауна для команды
@purge.error
async def purge_error(inter: disnake.CommandInteraction, error):
    if isinstance(error, commands.CommandOnCooldown):
        await inter.response.send_message(f"Вы можете использовать эту команду снова через {error.retry_after:.2f} секунд.", ephemeral=True)

async def send_webhook(webhook_url, embed=None, content=None):
    async with aiohttp.ClientSession() as session:
        webhook = disnake.Webhook.from_url(webhook_url, session=session)
        if embed:
            await webhook.send(embed=embed)
        elif content:
            await webhook.send(content)


@bot.slash_command(name='restart', description='Перезагрузить бота')
@commands.is_owner()
async def restart(interaction: disnake.ApplicationCommandInteraction):
    await interaction.response.send_message("Перезагрузка бота...")
    os.execv(sys.executable, ['python'] + sys.argv)


@bot.command()
@commands.is_owner()
async def update(ctx):
    await ctx.send("Начинаю обновление...")

    try:
        os.chdir('C:\\Users\\cooki\\Desktop\\Homework\\soullesscoffee')

        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Обновление бота'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)

        await ctx.send("Обновление завершено успешно!")
    except subprocess.CalledProcessError as e:
        await ctx.send(f"Произошла ошибка при обновлении: {e}")

bot.run(settings['token'])
