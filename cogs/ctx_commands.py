import disnake
from disnake.ext import commands

class Ctx_commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="say", aliases=["s"])
    async def say_command(self, ctx, arg):
        await ctx.send(arg)

def setup(bot):
    bot.add_cog(Ctx_commands(bot))

print('Модуль "Commands", загружен')