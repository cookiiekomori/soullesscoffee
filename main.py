from imports import *


def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

settings = load_config()

intents = disnake.Intents().all()
intents.message_content = True
intents.voice_states = True
intents.guilds = True 
bot = commands.Bot(command_prefix=settings['prefix'], intents=intents)

print("Идет процесс запуска, ожидайте...")

@tasks.loop(seconds=15)
async def update_voice_channel_name():
    total_members = 0

    for guild in bot.guilds:
        for channel in guild.voice_channels:
            total_members += len(channel.members)

    target_voice_channel = bot.get_channel(settings['TARGET_VOICE_CHANNEL_ID'])
    if target_voice_channel:
        new_name = f'🍥 » В войсе {total_members}'

        try:
            await target_voice_channel.edit(name=new_name)
        except disnake.errors.DiscordServerError as e:
            print(f"Ошибка при редактировании канала: {e}. Повторная попытка через 5 секунд.")
            await asyncio.sleep(60) 
            await update_voice_channel_name() 

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


for filename in os.listdir("cogs"):
    if filename.endswith(".py"):
        bot.load_extension("cogs." + filename[:-3])

def get_cogs():
    return [filename[:-3] for filename in os.listdir("cogs") if filename.endswith(".py")]

def is_owner():
    async def predicate(interaction: disnake.CommandInteraction):
        if interaction.user.id != bot.owner_id:
            await interaction.response.send_message("У вас нет доступа к этой команде.", ephemeral=True)
            return False
        return True
    return commands.check(predicate)

class Cogs(str, Enum):
    """Список модулей"""
    CtxCommands = 'ctx_commands'
    Embed = 'embed'
    FunCommands = 'fun_commands'
    Inform = 'inform'
    Logging = 'logging'
    Utils = 'utils'
    Data = "data"
    Tickets = "tickets"

# Загрузка модуля ------------------------------------------------------------------------------------------------------------
@bot.slash_command(guild_ids=[854309914788626442], description="Загрузить модуль бота")
@commands.is_owner()
async def load(inter: disnake.CommandInteraction, 
                module: Cogs = disnake.Option(name="module", 
                                               description="Выберите модуль для загрузки", 
                                               choices=[cog for cog in Cogs])):
    try:
        bot.load_extension(f"cogs.{module}")
        await inter.response.send_message(f"Загружен модуль `{module}`", ephemeral=True)
        print(f"Загружен модуль {module}")
        
    except Exception as e:
        await inter.response.send_message(f"Ошибка при загрузке модуля `{module}`: {e}", ephemeral=True)

# Выгрузка модуля ------------------------------------------------------------------------------------------------------------
@bot.slash_command(guild_ids=[854309914788626442], description="Выгрузить модуль бота")
@commands.is_owner()
async def unload(inter: disnake.CommandInteraction, 
                  module: Cogs = disnake.Option(name="module", 
                                                 description="Выберите модуль для выгрузки", 
                                                 choices=[cog for cog in Cogs])):
    try:
        bot.unload_extension(f"cogs.{module}")
        await inter.response.send_message(f"Выгружен модуль `{module}`", ephemeral=True)
        print(f"Выгружен модуль {module}")
        
    except Exception as e:
        await inter.response.send_message(f"Ошибка при выгрузке модуля `{module}`: {e}", ephemeral=True)

# Перезагрузка модуля ------------------------------------------------------------------------------------------------------------
@bot.slash_command(guild_ids=[854309914788626442], description="Перезагрузить модуль бота")
@commands.is_owner()
async def reload(inter: disnake.CommandInteraction, 
                  module: Cogs = disnake.Option(name="module", 
                                                 description="Выберите модуль для перезагрузки", 
                                                 choices=[cog for cog in Cogs])):
    try:
        bot.reload_extension(f"cogs.{module}")
        await inter.response.send_message(f"Перезагружен модуль `{module}`", ephemeral=True)
        print(f"Перезагружен модуль {module}")
        
    except Exception as e:
        await inter.response.send_message(f"Ошибка при перезагрузке модуля `{module}`: {e}", ephemeral=True)


bot.run(settings['token'])
