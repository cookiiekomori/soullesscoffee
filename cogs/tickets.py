from imports import *

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

settings = load_config()
WEBHOOK_URL = settings['webhook_url']['command_log']

class ReportModal(disnake.ui.Modal):
    def __init__(self, user: disnake.User):
        components = [
            disnake.ui.TextInput(
                label="Причина репорта",
                placeholder="Введите причину...",
                custom_id="report_reason",
                style=disnake.TextInputStyle.paragraph,
                required=True,
                max_length=200,
            ),
        ]
        super().__init__(title=f"Репорт {user}", custom_id="report_user", components=components)
        self.user = user

    async def callback(self, interaction: disnake.ModalInteraction):
        reason = interaction.text_values["report_reason"]
        member = self.user.mention

        embed = disnake.Embed(
            title="Новый репорт",
            color=disnake.Color.from_rgb(43, 45, 49)  # Переместил color сюда
        )

        embed.add_field(name="Отправил", value=interaction.user.mention, inline=True)
        embed.add_field(name="На кого", value=f"{self.user.mention}", inline=True)
        embed.add_field(name="Причина", value=f"```{reason}```", inline=False)

        async with aiohttp.ClientSession() as session:
            webhook = disnake.Webhook.from_url(WEBHOOK_URL, session=session)
            await webhook.send(embed=embed)

        await interaction.response.send_message(f"Пользователь {self.user.mention} был репортнут за:\n{reason}", ephemeral=True)

class ReportCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Модуль {self.__class__.__name__} подключен.")

    @commands.slash_command(name="report", description="Репорт пользователя")
    async def report(self, interaction: disnake.ApplicationCommandInteraction, user: disnake.User):
        """Отправка репорта"""
        modal = ReportModal(user)
        await interaction.response.send_modal(modal)

def setup(bot):
    bot.add_cog(ReportCog(bot))
