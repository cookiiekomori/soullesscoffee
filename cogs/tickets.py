from imports import *

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

settings = load_config()
WEBHOOK_URL = settings['webhook_url']['command_log']  # Замените на ваш URL вебхука

class ReportModal(disnake.ui.Modal):
    def __init__(self, user: disnake.User):
        components = [
            disnake.ui.TextInput(
                label="Reason for reporting",
                placeholder="Enter the reason...",
                custom_id="report_reason",
                style=disnake.TextInputStyle.paragraph,
                required=True,
                max_length=200,
            ),
        ]
        super().__init__(title=f"Report {user}", custom_id="report_user", components=components)
        self.user = user  # Сохраняем пользователя, на которого подается репорт

    async def callback(self, interaction: disnake.ModalInteraction):
        reason = interaction.text_values["report_reason"]
        
        # Создание эмбеда
        embed = disnake.Embed(
            title="User Report",
            description=f"Reported {self.user.mention} for: {reason}",
            color=disnake.Color.from_rgb(43, 45, 49)
        )

        # Отправка данных о репорте через вебхук
        async with aiohttp.ClientSession() as session:
            webhook = disnake.Webhook.from_url(WEBHOOK_URL, session=session)
            await webhook.send(embed=embed)

        await interaction.response.send_message(f"Reported {self.user.mention} for: {reason}", ephemeral=True)

class ReportCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="report", description="Report a user")
    async def report(self, interaction: disnake.ApplicationCommandInteraction, user: disnake.User):
        """Report a user with a reason."""
        modal = ReportModal(user)
        await interaction.response.send_modal(modal)

def setup(bot):
    bot.add_cog(ReportCog(bot))
