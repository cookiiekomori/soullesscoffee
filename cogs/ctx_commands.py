from imports import *

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

settings = load_config()


class CTX_Commands(commands.Cog):
    """Модуль, от которого скоро избавлюсь"""
    def __init__(self, bot):
        self.bot = bot

        self.developer_role_id = settings['roles']['developer']['role_id']
        self.admin_role_id = settings['roles']['admin']['role_id']
        self.helper_role_id = settings['roles']['helper']['role_id']

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Модуль {self.__class__.__name__} подключен.")

    @commands.command(name="say", aliases=["s"], help=f"Отправляет сообщение от имени бота. Используйте: `{settings['prefix']}say <сообщение>`.")
    async def say_command(self, ctx, *, arg=None):
        owner_id = self.bot.owner_id
        allowed_role_ids = *self.admin_role_id, self.developer_role_id, *self.helper_role_id
        if ctx.author.id != owner_id and not any(role.id in allowed_role_ids for role in ctx.author.roles):
            await ctx.send("Недостаточно прав для использования этой команды.")
            return
        if arg is None:
            await ctx.send("Ошибка ввода: Неверный аргумент.")
        else:
            await ctx.send(arg)

    @commands.command(name="send_to", help=f"Отправляет сообщение в указанный канал. Используйте: `{settings['prefix']}send_to <канал_id> <сообщение>`.")
    async def send_to_command(self, ctx, channel_id: int, *, message=None):
        owner_id = self.bot.owner_id
        allowed_role_ids = *self.admin_role_id, self.developer_role_id # руководители, девелоп
        if ctx.author.id != owner_id and not any(role.id in allowed_role_ids for role in ctx.author.roles):
            await ctx.send("Недостаточно прав для использования этой команды.")
            return

        if message is None:
            await ctx.send("Ошибка ввода: Неверный аргумент.")
            return
        
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            await ctx.send("Ошибка: Канал не найден.")
            return
        
        await channel.send(message)
        await ctx.send(f"Сообщение отправлено в канал {channel.mention}.")

def setup(bot):
    bot.add_cog(CTX_Commands(bot))
