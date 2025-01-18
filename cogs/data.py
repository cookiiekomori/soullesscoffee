from imports import *


def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


settings = load_config()


class Data(commands.Cog):
    """База данных"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Модуль {self.__class__.__name__} подключен.")

    @commands.command(name="update_base_of_profiles", help=f"Обновление базы данных пользователей(Админ команда)")
    async def update_base_of_profiles(self, ctx, arg=None):
        if ctx.author.id == 1180074901110005841 or 528724400850206720:
            for guild in self.bot.guilds:
                for member in guild.members:
                    if not member.bot:
                        df = pd.read_csv('Bases\\base_of_profiles.csv')
                        in_data = df[(df["Guild_id"] == guild.id) & (df["User_id"] == member.id)]
                        if in_data.empty:
                            df.loc[len(df)] = [guild.id, guild.name, member.name, member.id]
                        df.to_csv('Bases\\base_of_profiles.csv', index=False)
        else:
            await ctx.send("Недостаточно прав для использования этой команды!")


def setup(bot):
    bot.add_cog(Data(bot))
