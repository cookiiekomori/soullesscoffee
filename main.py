import disnake
import os
import asyncio
from disnake.ext import commands
import json
import aiohttp

# Загрузка конфигурации
def load_config():
    with open('C:\\Users\\cooki\\Desktop\\Homework\\soullesscoffee\\config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Сохранение конфигурации
def save_config(config):
    with open('C:\\Users\\cooki\\Desktop\\Homework\\soullesscoffee\\config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

# Загрузка конфигурации
settings = load_config()  # Здесь вы загружаете данные из JSON в переменную settings

# Создание бота
intents = disnake.Intents().all()
intents.message_content = True
bot = commands.Bot(command_prefix=settings['prefix'], intents=intents)

print("Идет процесс запуска, ожидайте...")

@bot.event
async def on_ready():
    print(f"-------------------------\nУспешно запущен бот, {bot.user.name}")
    bot.loop.create_task(status_task(bot))

@bot.event
async def on_command(ctx):
    print(f"Команда '{ctx.command}' была вызвана пользователем {ctx.author} в канале {ctx.channel}.")

@bot.event
async def on_command_error(ctx, error):
    print(f"Ошибка при выполнении команды '{ctx.command}': {error}")

async def status_task(bot):
    statuses = [
        f"{len(bot.users)} users on {len(bot.guilds)} guilds",
        "куки",
        f"use {settings['prefix']}help for help"
    ]
    while True:
        for status in statuses:
            await bot.change_presence(activity=disnake.Streaming(type=1, url="https://www.twitch.tv/videos/225796573?t=00h00m30s", name=status))
            await asyncio.sleep(15)

# Загрузка модулей
for filename in os.listdir("C:\\Users\\cooki\\Desktop\\Homework\\soullesscoffee\\cogs"):
    if filename.endswith(".py"):
        bot.load_extension("cogs." + filename[:-3])

cogs = [filename[:-3] for filename in os.listdir("C:\\Users\\cooki\\Desktop\\Homework\\soullesscoffee\\cogs") if filename.endswith(".py")]

@bot.slash_command(description="Выводит список доступных модулей")
@commands.is_owner()
async def list_cogs(inter: disnake.CommandInteraction):
    cog_list = "\n".join(cogs)
    await inter.response.send_message(f"Список модулей:```\n{cog_list}\n```", ephemeral=True)

@bot.slash_command(description="Загрузить модуль бота")
@commands.is_owner()
async def load(inter: disnake.CommandInteraction, module: str):
    try:
        bot.load_extension(f"cogs.{module}")
        await inter.response.send_message(f"Загружен модуль `{module}`", ephemeral=True)
    except Exception as e:
        await inter.response.send_message(f"Ошибка при загрузке модуля `{module}`: {e}", ephemeral=True)

@bot.slash_command(description="Выгрузить модуль бота")
@commands.is_owner()
async def unload(inter: disnake.CommandInteraction, module: str):
    try:
        bot.unload_extension(f"cogs.{module}")
        await inter.response.send_message(f"Выгружен модуль `{module}`", ephemeral=True)
    except Exception as e:
        await inter.response.send_message(f"Ошибка при выгрузке модуля `{module}`: {e}", ephemeral=True)

@bot.slash_command(description="Перезагрузить модуль бота")
@commands.is_owner()
async def reload(inter: disnake.CommandInteraction, module: str):
    try:
        bot.reload_extension(f"cogs.{module}")
        await inter.response.send_message(f"Перезагружен модуль `{module}`", ephemeral=True)
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

# Запуск бота
bot.run(settings['token'])
