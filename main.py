import disnake
import os
import asyncio
from disnake.ext import commands 
from config import settings


intents = disnake.Intents().all()
intents.message_content = True
bot = commands.Bot(command_prefix=settings['prefix'], intents=intents)

@bot.event
async def on_ready():
	print(
	"Успешно запущен бот, " + f'{bot.user.name}')
	bot.loop.create_task(status_task(bot))

async def status_task(bot):
	while True:
		await bot.change_presence(activity=disnake.Streaming(type=1, url="https://www.twitch.tv/videos/225796573?t=00h00m30s", name=f"{len(bot.users)} users on {len(bot.guilds)} guilds"))
		await asyncio.sleep(15)
		await bot.change_presence(activity=disnake.Streaming(type=1, url="https://www.twitch.tv/videos/225796573?t=00h00m30s", name=f"куки"))
		await asyncio.sleep(15)
		await bot.change_presence(activity=disnake.Streaming(type=1, url="https://www.twitch.tv/videos/225796573?t=00h00m30s", name=f"use {settings['prefix']} for help"))
		await asyncio.sleep(15)

for filename in os.listdir("./cogs"):
	if filename.endswith(".py"):
		bot.load_extension("cogs." + filename[:-3])


@bot.slash_command(description='Загрузить модуль бота')
@commands.is_owner()
async def load(inter: disnake.CommandInteraction, module: str = commands.Param(name="module", description="Название модуля")):
	bot.load_extension(f"cogs.{module}")
	await inter.response.send_message(f"Загружен модуль `{module}`",ephemeral=True)

@bot.slash_command(description='Выгрузить модуль бота')
@commands.is_owner()
async def unload(inter: disnake.CommandInteraction, module: str = commands.Param(name="module", description="Название модуля")):
	bot.unload_extension(f"cogs.{module}")
	await inter.response.send_message(f"Выгружен модуль `{module}`",ephemeral=True)
    
@bot.slash_command(description="Перезагрузить модуль бота")
@commands.is_owner()
async def reload(inter: disnake.CommandInteraction, module: str = commands.Param(name="module", description="Название модуля")):
	bot.reload_extension(f"cogs.{module}")
	await inter.response.send_message(f"Перезагружен модуль `{module}`",ephemeral=True)


bot.run(settings['token'])