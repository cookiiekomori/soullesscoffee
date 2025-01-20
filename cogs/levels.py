from imports import *

class Experience(commands.Cog):
    def __init__(self, bot, db_manager):
        self.bot = bot
        self.db_manager = db_manager

    def get_user_level(self, guild_id, user_id):
        user_data = self.db_manager.get_user_data(guild_id, user_id)
        if user_data is not None:
            experience = user_data['experience']
            level = user_data['level']
            formatted_level = str(level).zfill(3) 
            return experience, formatted_level
        return 0, "000"

    def update_user_level(self, guild_id, user_id, exp_gain):
        self.db_manager.update_user_data(guild_id, user_id, exp_gain=exp_gain)
        experience, _ = self.get_user_level(guild_id, user_id)
        level = int((experience ** 0.2))
        self.db_manager.update_user_data(guild_id, user_id, exp_gain=None, about_me=None, level=level)


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        self.update_user_level(message.guild.id, message.author.id, 10)

def setup(bot, db_manager):
    bot.add_cog(Experience(bot, db_manager))