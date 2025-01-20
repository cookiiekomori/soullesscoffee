from imports import *

class TicketCog(commands.Cog):
    def __init__(self, bot, db_manager):
        self.bot = bot
        self.base_path = "Bases/base_of_tickets.csv"

        if os.path.exists(self.base_path):
            self.ticket_data = pd.read_csv(self.base_path)
            self.ticket_data['Number_id'] = pd.to_numeric(self.ticket_data['Number_id'], errors='coerce').fillna(0).astype(int)
            max_ticket_number = self.ticket_data['Number_id'].max()
            self.current_ticket_number = int(max_ticket_number) if pd.notna(max_ticket_number) else 0
        else:
            self.current_ticket_number = 0
            self.ticket_data = pd.DataFrame(columns=['Guild_id', 'User_id', 'Number_id', 'Support_Role_ID', 'Ticket_Channel_ID'])
            self.ticket_data.to_csv(self.base_path, index=False)

        # Загрузка информации о канале и роли поддержки
        self.ticket_channel_id = self.ticket_data['Ticket_Channel_ID'].iloc[0] if not self.ticket_data.empty else None
        self.SUPPORT_ROLE_ID = self.ticket_data['Support_Role_ID'].iloc[0] if not self.ticket_data.empty else None

    def update_ticket_data(self):
        """Обновляет CSV-файл с данными о тикетах."""
        self.ticket_data.to_csv(self.base_path, index=False)

    @commands.slash_command(name="setup_ticket", description="Настроить систему тикетов")
    async def setup_ticket(self, interaction: disnake.ApplicationCommandInteraction, support_role: disnake.Role):
        guild = interaction.guild

        # Проверяем, существует ли канал для тикетов
        ticket_channel = self.bot.get_channel(self.ticket_channel_id)

        if ticket_channel is None:
            # Если канал не существует, создаем новый
            ticket_channel = await guild.create_text_channel('🍥тикеты')
            self.ticket_channel_id = ticket_channel.id

        # Сохранение роли поддержки и канала в CSV
        self.SUPPORT_ROLE_ID = support_role.id
        self.ticket_data = pd.DataFrame({
            'Guild_id': [interaction.guild.id],
            'User_id': [interaction.user.id],
            'Number_id': [self.current_ticket_number],
            'Support_Role_ID': [self.SUPPORT_ROLE_ID],
            'Ticket_Channel_ID': [self.ticket_channel_id]
        })
        self.update_ticket_data()

        embed = disnake.Embed(
            title="Обращение",
            description="Если вы хотите обратиться к администрации, нажмите кнопку ниже, чтобы создать тикет.",
            color=disnake.Color.from_rgb(43, 45, 49)
        )
        embed.set_image(url="https://i.imgur.com/8zBMq5O.png")
        button = disnake.ui.Button(label="🍥 » Создать тикет", style=disnake.ButtonStyle.green)

        # Создаем View и добавляем кнопку
        view = disnake.ui.View()
        view.add_item(button)

        # Создаем View и добавляем кнопку
        view = disnake.ui.View()
        view.add_item(button)

        async def button_callback(interaction: disnake.MessageInteraction):
            text_input = disnake.ui.TextInput(
                label="Опишите вашу проблему",
                style=disnake.TextInputStyle.paragraph,
                required=True,
                custom_id="ticket_description"
            )
            modal = disnake.ui.Modal(title="Создание тикета", components=[text_input])

            await interaction.response.send_modal(modal)
            try:
                modal_interaction = await self.bot.wait_for(
                    "modal_submit",
                    check=lambda i: (
                        print(f"Проверка: custom_id = {i.custom_id}, user = {i.user}, ожидаемый user = {interaction.user}"),
                        i.custom_id == "ticket_description" and i.user == interaction.user
                    ),
                    timeout=60.0
                )
            except asyncio.TimeoutError:
                await interaction.send("Время ожидания истекло. Пожалуйста, попробуйте снова.", ephemeral=True)
                return
            except Exception as e:
                return

            ticket_description = modal_interaction.text_values['ticket_description']

            # Закрываем модальное окно, отправляя ответ
            await modal_interaction.send("Обработка вашего тикета...", ephemeral=True)

            ticket_channel = self.bot.get_channel(self.ticket_channel_id)
            if ticket_channel is None:
                await modal_interaction.send("Канал для тикетов не найден.", ephemeral=True)
                return

            self.current_ticket_number += 1
            ticket_number = f"{self.current_ticket_number:04d}"
            try:
                message = await ticket_channel.send(
                    f"Тикет #{ticket_number} открыт пользователем {modal_interaction.user.mention}.\n\n{ticket_description}"
                )
                thread = await message.create_thread(
                    name=f'ticket-{ticket_number}',
                    auto_archive_duration=60 
                )
                await message.delete()
                await thread.send(f"{modal_interaction.user.mention} <@&{self.SUPPORT_ROLE_ID}>")
                embed = disnake.Embed(title=f"Новый тикет #{ticket_number}", color=disnake.Color.from_rgb(43, 45, 49))
                embed.add_field(name="Автор", value=f"{modal_interaction.user.name} ({modal_interaction.user.mention})", inline=False)
                embed.add_field(name="Описание проблемы", value=f"```\n{ticket_description}\n```", inline=False)
                await thread.send(embed=embed)

                new_ticket_entry = pd.DataFrame({
                    'Guild_id': [interaction.guild.id],
                    'User_id': [modal_interaction.user.id],
                    'Number_id': [ticket_number],
                    'Support_Role_ID': [self.SUPPORT_ROLE_ID],
                    'Ticket_Channel_ID': [self.ticket_channel_id]
                })
                self.ticket_data = pd.concat([self.ticket_data, new_ticket_entry], ignore_index=True)
                self.update_ticket_data() 

            except Exception as e:
                await modal_interaction.send("Не удалось создать ветку для тикета. Пожалуйста, попробуйте снова.", ephemeral=True)
                return

            await modal_interaction.send(f"Ваш тикет #{ticket_number} был успешно создан!", ephemeral=True)


        button.callback = button_callback
        view = disnake.ui.View()
        view.add_item(button)

        await ticket_channel.send(embed=embed, view=view)
        await interaction.send("Система тикетов настроена!", ephemeral=True)

    @commands.slash_command(name="close_ticket", description="Закрыть тикет")
    async def close_ticket(self, interaction: disnake.ApplicationCommandInteraction):
        # Проверяем, является ли текущий канал веткой
        if interaction.channel and interaction.channel.type == disnake.ChannelType.public_thread:
            await interaction.send("Спасибо за обращение! Тикет будет закрыт.", ephemeral=True)
            await interaction.channel.delete()
        else:
            await interaction.send("Эта команда может быть использована только в ветках тикетов.", ephemeral=True)

    @commands.Cog.listener()
    async def on_channel_delete(self, channel):
        # Проверяем, является ли удаленный канал каналом для тикетов
        if channel.id == self.ticket_channel_id:
            # Удаляем все записи, связанные со старым каналом из базы
            self.ticket_data = self.ticket_data[self.ticket_data['Ticket_Channel_ID'] != self.ticket_channel_id]
            self.update_ticket_data()  # Обновляем CSV-файл

            # Создаем новый канал для тикетов
            guild = channel.guild
            new_ticket_channel = await guild.create_text_channel('ticket-channel')
            self.ticket_channel_id = new_ticket_channel.id

            # Обновляем данные о канале в базе
            self.ticket_data['Ticket_Channel_ID'] = self.ticket_channel_id
            self.update_ticket_data()


def setup(bot, db_manager):
    bot.add_cog(TicketCog(bot, db_manager))
