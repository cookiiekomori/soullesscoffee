from imports import *

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

settings = load_config()

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webhook_urls = settings['webhook_url']
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Модуль {self.__class__.__name__} подключен.")
        
    async def send_webhook(self, log_type: str, embed: disnake.Embed):
        webhook_url = self.webhook_urls.get(log_type)
        if webhook_url:
            async with aiohttp.ClientSession() as session:
                webhook = disnake.Webhook.from_url(webhook_url, session=session)
                await webhook.send(embed=embed)


# Логи использования команд бота ------------------------------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_command(self, ctx):
        embed = disnake.Embed(
            title=f"Использование команды: `{ctx.command}`",
            color=disnake.Color.green()
        )
        embed.add_field(name="Пользователь", value=ctx.author.mention, inline=True)
        embed.add_field(name="Канал", value=ctx.channel.mention, inline=True)

        if ctx.command.name == "say":
            additional_info = f"Текст:\n```{ctx.message.content[len(ctx.prefix) + len(ctx.command.name):].strip()}```"
            embed.add_field(name="Дополнительная информация", value=additional_info, inline=False)

        embed.set_image(url=settings['logging_image']['command_log'])
        await self.send_webhook("command_log", embed)

# Логи по сообщениям ------------------------------------------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author == self.bot.user:
            return 
        embed = disnake.Embed(
            title="Сообщение было удалено",
            description=f"Текст сообщения:\n```{message.content}```",
            color=disnake.Color.from_rgb(204, 5, 114)
        )
        embed.add_field(name="Пользователь", value=message.author.mention, inline=True) 
        embed.add_field(name="Канал", value=message.channel.mention, inline=True) 
        embed.set_image(url=settings['logging_image']['message_log'])
        await self.send_webhook("message_log", embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        embed = disnake.Embed(
            title="Сообщение было отредактировано",
            description=f"Старый текст:\n```{before.content}```\nНовый текст:\n```{after.content}```",
            color=disnake.Color.from_rgb(219, 140, 84)
        )
        embed.add_field(name="Пользователь", value=before.author.mention, inline=True)
        embed.add_field(name="Канал", value=before.channel.mention, inline=True)
        embed.set_image(url=settings['logging_image']['message_log'])
        await self.send_webhook("message_log", embed)

# Логи входа и выхода с сервера -------------------------------------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"{member.name} присоединился к серверу.")
        embed = disnake.Embed(
            title="Пользователь присоединился к серверу",
            color=disnake.Color.green()
        )
        embed.add_field(name="Пользователь", value=member.mention, inline=True)
        embed.add_field(name="Сервер", value=member.guild.name, inline=True)
        embed.set_image(url=settings['logging_image']['member_join_remove_log'])
        await self.send_webhook("member_join_remove_log", embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = disnake.Embed(
            title="Пользователь покинул сервер",
            color=disnake.Color.red()
        )
        embed.add_field(name="Пользователь", value=member.mention, inline=True)
        embed.add_field(name="Сервер", value=member.guild.name, inline=True)
        embed.set_image(url=settings['logging_image']['member_join_remove_log']) 
        await self.send_webhook("member_join_remove_log", embed)

# ------------------------------------------------------------------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            embed = disnake.Embed(
                title="Пользователь вошел в голосовой канал",
                color=disnake.Color.from_rgb(51, 235, 144)
            )
            embed.add_field(name="Пользователь", value=member.mention, inline=True)
            embed.add_field(name="Канал", value=after.channel.mention, inline=True)
            embed.set_image(url=settings['logging_image']['voice_join_leave_log'])
            await self.send_webhook("voice_join_leave_log", embed)
        elif before.channel is not None and after.channel is None:
            embed = disnake.Embed(
                title="Пользователь вышел из голосового канала",
                color=disnake.Color.from_rgb(219, 92, 83)
            )
            embed.add_field(name="Пользователь", value=member.mention, inline=True) 
            embed.add_field(name="Канал", value=before.channel.mention, inline=True)
            embed.set_image(url=settings['logging_image']['voice_join_leave_log'])
            await self.send_webhook("voice_join_leave_log", embed)

# Логи редактирования ролей на сервере ------------------------------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        embed = disnake.Embed(
            title="Была создана роль",
            color=disnake.Color.blue()
        )
        audit_logs = await role.guild.audit_logs(limit=1, action=disnake.AuditLogAction.role_create).flatten()
        user = audit_logs[0].user if audit_logs else None
        embed.add_field(name="Название", value=f"```{role.name}```", inline=True) 
        embed.add_field(name="Создатель", value=user.mention if user else "Неизвестный", inline=True)
        embed.set_image(url=settings['logging_image']['role_change_log']) 
        await self.send_webhook("role_change_log", embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        if role.guild is None:
            return 

        embed = disnake.Embed(
            title="Удаление роли",
            color=disnake.Color.red()
        )

        try:
            audit_logs = await role.guild.audit_logs(limit=1, action=disnake.AuditLogAction.role_delete).flatten()
            user = audit_logs[0].user if audit_logs else None
        except disnake.NotFound:
            return 
        except disnake.Forbidden:
            user = None
            print("Недостаточно прав для доступа к журналам аудита.")
        except Exception as e:
            user = None
            print(f"Произошла ошибка при получении журналов аудита: {str(e)}")

        embed.add_field(name="Название", value=f"```{role.name}```", inline=True)
        embed.add_field(name="Удалил", value=user.mention if user else "Неизвестный", inline=True)
        embed.set_image(url=settings['logging_image']['role_change_log']) 
        await self.send_webhook("role_change_log", embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):

        if before.id != after.id:
            return 

        if before.position != after.position:
            return 

        audit_logs = await before.guild.audit_logs(limit=1, action=disnake.AuditLogAction.role_update).flatten()
        user = audit_logs[0].user if audit_logs else None

        embed = disnake.Embed(
            title="Изменение роли",
            color=disnake.Color.orange()
        )

        if before.name != after.name:
            embed.add_field(name="Была", value=f"```{before.name}```", inline=True)
            embed.add_field(name="Стала", value=f"```{after.name}```", inline=True)

        if before.color != after.color:
            old_color_hex = f"#{before.color.r:02x}{before.color.g:02x}{before.color.b:02x}"
            new_color_hex = f"#{after.color.r:02x}{after.color.g:02x}{after.color.b:02x}"
            embed.add_field(name="Изменение цвета", value=f"Старый цвет: ``{old_color_hex}``\nНовый цвет: ``{new_color_hex}``", inline=True)

        if embed.fields:
            embed.add_field(name="Изменил", value=user.mention if user else "Неизвестный", inline=True)
            embed.set_image(url=settings['logging_image']['role_change_log'])
            await self.send_webhook("role_change_log", embed)

# Логи изменения ролей у пользователей -----------------------------------------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.guild is None:
            return

        added_roles = [role for role in after.roles if role not in before.roles]
        removed_roles = [role for role in before.roles if role not in after.roles]

        for role in added_roles:
            embed = disnake.Embed(
                title="Добавление роли пользователю",
                color=disnake.Color.green()
            )
            try:
                audit_logs = await after.guild.audit_logs(limit=1, action=disnake.AuditLogAction.member_role_update).flatten()
                executor = audit_logs[0].user if audit_logs else None
            except disnake.NotFound:
                executor = None
                print("Гильдия не найдена.")
            except disnake.Forbidden:
                executor = None
                print("Недостаточно прав для доступа к журналам аудита.")
            except Exception as e:
                executor = None
                print(f"Произошла ошибка при получении журналов аудита: {str(e)}")

            embed.add_field(name="Название", value=f"```{role.name}```", inline=False) 
            embed.add_field(name="Кому добавили", value=after.mention, inline=True)  
            embed.add_field(name="Кто добавил", value=executor.mention if executor else "Неизвестный", inline=True) 
            embed.set_image(url=settings['logging_image']['role_member_change_log'])
            await self.send_webhook("role_member_change_log", embed)

        for role in removed_roles:
            embed = disnake.Embed(
                title="Удаление роли у пользователя",
                color=disnake.Color.red()
            )
            try:
                audit_logs = await after.guild.audit_logs(limit=1, action=disnake.AuditLogAction.member_role_update).flatten()
                executor = audit_logs[0].user if audit_logs else None
            except disnake.NotFound:
                executor = None
                print("Гильдия не найдена.")
            except disnake.Forbidden:
                executor = None
                print("Недостаточно прав для доступа к журналам аудита.")
            except Exception as e:
                executor = None
                print(f"Произошла ошибка при получении журналов аудита: {str(e)}")

            embed.add_field(name="Название", value=f"```{role.name}```", inline=False) 
            embed.add_field(name="У кого удалили", value=after.mention, inline=True) 
            embed.add_field(name="Кто удалил", value=executor.mention if executor else "Неизвестный", inline=True) 
            embed.set_image(url=settings['logging_image']['role_member_change_log'])
            await self.send_webhook("role_member_change_log", embed)

# Логи перемещения бота по серверам -------------------------------------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        embed = disnake.Embed(
            title="Бот выгнан с сервера",
            description=f"Бот был выгнан с сервера **{guild.name}**",
            color=disnake.Color.red()
        )
        embed.set_image(url=settings['logging_image']['bot_guild_log'])
        await self.send_webhook("bot_guild_log", embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        embed = disnake.Embed(
            title="Бот добавлен на сервер",
            description=f"Бот был добавлен на сервер **{guild.name}**",
            color=disnake.Color.green()
        )

        try:
            invite = await guild.text_channels[0].create_invite(max_age=300)
            embed.add_field(name="Ссылка на сервер", value=invite, inline=True)
        except disnake.Forbidden:
            embed.add_field(name="Ошибка", value="Не удалось создать ссылку на сервер (нет прав)", inline=True)
        except Exception as e:
            embed.add_field(name="Ошибка", value=f"Не удалось создать ссылку на сервер: {str(e)}", inline=True)

        embed.set_image(url=settings['logging_image']['bot_guild_log']) 
        await self.send_webhook("bot_guild_log", embed)

# Логи редактирования каналов ----------------------------------------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        channel_type = "Голосовой" if channel.type == disnake.ChannelType.voice else "Текстовый"
        embed = disnake.Embed(
            title=f"Был создан {channel_type} канал",
            color=disnake.Color.blue()
        )
        audit_logs = await channel.guild.audit_logs(limit=1, action=disnake.AuditLogAction.channel_create).flatten()
        user = audit_logs[0].user if audit_logs else None
        embed.add_field(name="Канал", value=channel.mention, inline=True)
        embed.add_field(name="Создатель", value=user.mention if user else "Неизвестный", inline=True)
        embed.set_image(url=settings['logging_image']['channel_change_log']) 
        await self.send_webhook("channel_change_log", embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        embed = disnake.Embed(
            title="Удаление канала",
            color=disnake.Color.red()
        )
        audit_logs = await channel.guild.audit_logs(limit=1, action=disnake.AuditLogAction.channel_delete).flatten()
        user = audit_logs[0].user if audit_logs else None
        embed.add_field(name="Название", value=f"```{channel.name}```", inline=True) 
        embed.add_field(name="Удалил", value=user.mention if user else "Неизвестный", inline=True)
        embed.set_image(url=settings['logging_image']['channel_change_log'])
        await self.send_webhook("channel_change_log", embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        embed = disnake.Embed(
            title="Изменение канала",
            color=disnake.Color.orange()
        )
        audit_logs = await before.guild.audit_logs(limit=1, action=disnake.AuditLogAction.channel_update).flatten()
        user = audit_logs[0].user if audit_logs else None

        if before.name != after.name:
            embed.add_field(name="Было", value=f"```{before.name}```", inline=True)
            embed.add_field(name="Стало", value=f"```{after.name}```", inline=True)

        if before.type != after.type:
            embed.add_field(name="Изменение типа канала", value=f"Старый тип: ``{before.type}``\nНовый тип: ``{after.type}``", inline=True)

        if embed.fields:
            embed.add_field(name="Изменил", value=user.mention if user else "Неизвестный", inline=False)
            embed.set_image(url=settings['logging_image']['channel_change_log'])
            await self.send_webhook("channel_change_log", embed)


    # Логи редактирования сервера -----------------------------------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        embed = disnake.Embed(
            title="Изменение сервера",
            color=disnake.Color.blue()
        )
        embed.set_image(url=settings['logging_image']['server_change_log'])

        if before.name != after.name:
            embed.add_field(name="Старое имя сервера", value=f"```{before.name}```", inline=True)
            embed.add_field(name="Новое имя сервера", value=f"```{after.name}```", inline=True)

        if before.icon != after.icon:
            embed.description = "Иконка сервера была изменена."

        if before.preferred_locale != after.preferred_locale:
            embed.add_field(name="Старая локализация", value=f"**{before.preferred_locale}**", inline=True)
            embed.add_field(name="Новая локализация", value=f"**{after.preferred_locale}**", inline=True)

        if len(embed.fields) > 0 or embed.description:
            await self.send_webhook("server_change_log", embed)




    # Логи редактирования эмодзи, стикеров ----------------------------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        added_emojis = [emoji for emoji in after if emoji not in before]
        for emoji in added_emojis:
            embed = disnake.Embed(
                title=f"Эмодзи '{emoji.name}' был добавлен на сервере '{guild.name}'",
                color=disnake.Color.green()
            )
            audit_logs = await guild.audit_logs(limit=1, action=disnake.AuditLogAction.emoji_create).flatten()
            executor = audit_logs[0].user if audit_logs else None
            embed.add_field(name="Добавил", value=executor.mention if executor else "Неизвестный", inline=False)
            await self.send_webhook("server_emoji_change_log", embed)

        removed_emojis = [emoji for emoji in before if emoji not in after]
        for emoji in removed_emojis:
            embed = disnake.Embed(
                title=f"Эмодзи '{emoji.name}' был удален на сервере '{guild.name}'",
                color=disnake.Color.red()
            )
            audit_logs = await guild.audit_logs(limit=1, action=disnake.AuditLogAction.emoji_delete).flatten()
            executor = audit_logs[0].user if audit_logs else None
            embed.add_field(name="Удалил", value=executor.mention if executor else "Неизвестный", inline=False)
            await self.send_webhook("server_emoji_change_log", embed)

    @commands.Cog.listener()
    async def on_sticker_create(self, sticker):
        embed = disnake.Embed(
            title=f"Стикер '{sticker.name}' был добавлен на сервере '{sticker.guild.name}'",
            color=disnake.Color.green()
        )
        audit_logs = await sticker.guild.audit_logs(limit=1, action=disnake.AuditLogAction.sticker_create).flatten()
        executor = audit_logs[0].user if audit_logs else None
        embed.add_field(name="Добавил", value=executor.mention if executor else "Неизвестный", inline=False)
        await self.send_webhook("server_emoji_change_log", embed)

    @commands.Cog.listener()
    async def on_sticker_delete(self, sticker):
        embed = disnake.Embed(
            title=f"Стикер '{sticker.name}' был удален на сервере '{sticker.guild.name}'",
            color=disnake.Color.red()
        )
        audit_logs = await sticker.guild.audit_logs(limit=1, action=disnake.AuditLogAction.sticker_delete).flatten()
        executor = audit_logs[0].user if audit_logs else None
        embed.add_field(name="Удалил", value=executor.mention if executor else "Неизвестный", inline=False)
        await self.send_webhook("server_emoji_change_log", embed)

    # Логи банов -----------------------------------------------------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if guild is None:
            return 

        embed = disnake.Embed(
            title="Пользователь забанен на сервере",
            color=disnake.Color.red()
        )
        embed.add_field(name="Пользователь", value=user.mention, inline=True)
        embed.add_field(name="Сервер", value=guild.name, inline=True)

        try:
            audit_logs = await guild.audit_logs(limit=1, action=disnake.AuditLogAction.ban).flatten()
            executor = audit_logs[0].user if audit_logs else None
            embed.add_field(name="Исполнитель", value=executor.mention if executor else "Неизвестный", inline=True)
        except disnake.Forbidden:
            embed.add_field(name="Исполнитель", value="Неизвестный", inline=True)
            print("Недостаточно прав для доступа к журналам аудита.")
        except Exception as e:
            embed.add_field(name="Исполнитель", value="Неизвестный", inline=True)
            print(f"Произошла ошибка при получении журналов аудита: {str(e)}")

        embed.set_image(url=settings['logging_image']['member_ban_log']) 
        await self.send_webhook("member_ban_log", embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        if guild is None:
            return

        embed = disnake.Embed(
            title="Пользователь разбанен на сервере",
            color=disnake.Color.green()
        )
        embed.add_field(name="Пользователь", value=user.mention, inline=True)
        embed.add_field(name="Сервер", value=guild.name, inline=True)

        try:
            audit_logs = await guild.audit_logs(limit=1, action=disnake.AuditLogAction.unban).flatten()
            executor = audit_logs[0].user if audit_logs else None
            embed.add_field(name="Исполнитель", value=executor.mention if executor else "Неизвестный", inline=True)
        except disnake.Forbidden:
            embed.add_field(name="Исполнитель", value="Неизвестный", inline=True)
            print("Недостаточно прав для доступа к журналам аудита.")
        except Exception as e:
            embed.add_field(name="Исполнитель", value="Неизвестный", inline=True)
            print(f"Произошла ошибка при получении журналов аудита: {str(e)}")

        embed.set_image(url=settings['logging_image']['member_ban_log']) 
        await self.send_webhook("member_ban_log", embed)

def setup(bot):
    bot.add_cog(Logging(bot))

