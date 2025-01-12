import disnake
from disnake.ext import commands
import json
import aiohttp

# Функция для загрузки конфигурации
def load_config():
    with open('C:\\Users\\cooki\\Desktop\\Homework\\soullesscoffee\\config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Загрузка конфигурации
settings = load_config()

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webhook_urls = settings['webhook_url']  # Получаем все вебхуки
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Модуль {self.__class__.__name__} подключен.")
        

    async def send_webhook(self, log_type: str, content: str = None, embed: disnake.Embed = None):
        webhook_url = self.webhook_urls.get(log_type)
        if webhook_url:
            async with aiohttp.ClientSession() as session:
                webhook = disnake.Webhook.from_url(webhook_url, session=session)
                await webhook.send(content=content, embed=embed)

    async def log_action(self, action: str, user: disnake.User, channel: disnake.TextChannel, log_type: str, additional_info: str = ""):
        embed_color = disnake.Color.default()  # Цвет по умолчанию

        # Определение цвета в зависимости от действия
        if action == "Сообщение было удалено":
            embed_color = disnake.Color.from_rgb(204, 5, 114) 
        elif action == "Сообщение было отредактировано":
            embed_color = disnake.Color.from_rgb(219, 140, 84)
        elif action == "Пользователь вошел в голосовой канал":
            embed_color = disnake.Color.from_rgb(51, 235, 144)
        elif action == "Пользователь вышел из голосового канала":
            embed_color = disnake.Color.from_rgb(219, 92, 83)

        embed = disnake.Embed(title=action, color=embed_color)
        embed.add_field(name="Пользователь", value=user.mention if user else "Неизвестный", inline=False)
        embed.add_field(name="Канал", value=channel.mention if channel else "Неизвестный", inline=False)
        embed.add_field(name="Дополнительная информация", value=additional_info, inline=False)

        await self.send_webhook(log_type, embed=embed)

    # Логи по сообщениям ----------
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author == self.bot.user:
            return  # Игнорируем сообщения, удаленные ботом
        action = "Сообщение было удалено"
        additional_info = f"Текст сообщения:\n```{message.content}```"
        await self.log_action(action, message.author, message.channel, "message_delete_log", additional_info)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:  # Игнорируем сообщения, редактированные любым ботом
            return
        action = "Сообщение было отредактировано"
        additional_info = f"Старый текст:\n```{before.content}```\nНовый текст:\n```{after.content}```"
        await self.log_action(action, before.author, before.channel, "message_edit_log", additional_info)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        action = f"Команда '{ctx.command}' была вызвана"
        if ctx.command.name == "say":
            additional_info = f"Текст:\n```{ctx.message.content[len(ctx.prefix) + len(ctx.command.name):].strip()}```"
            await self.log_action(action, ctx.author, ctx.channel, "command_log", additional_info)
        else:
            await self.log_action(action, ctx.author, ctx.channel, "command_log")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        action = f"Пользователь присоединился к серверу"
        await self.log_action(action, member, member.guild.system_channel, "member_join_log")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        try:
            audit_logs = await member.guild.audit_logs(limit=1, action=disnake.AuditLogAction.kick).flatten()
            
            if audit_logs and audit_logs[0].target.id == member.id:
                action = f"Пользователь '{member.name}' был кикнут"
                executor = audit_logs[0].user if audit_logs else None
                await self.log_action(action, executor, member.guild.system_channel, "member_remove_log")
            else:
                action = f"Пользователь '{member.name}' покинул сервер"
                await self.log_action(action, None, member.guild.system_channel, "member_remove_log")
        except Exception as e:
            print(f"Произошла ошибка в on_member_remove: {e}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            action = f"Пользователь вошел в голосовой канал"
            await self.log_action(action, member, after.channel, "voice_join_log")
        elif before.channel is not None and after.channel is None:
            action = f"Пользователь вышел из голосового канала"
            await self.log_action(action, member, before.channel, "voice_leave_log")

    # Логи редактирования ролей ----------
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        action = f"Роль '{role.name}' была создана на сервере '{role.guild.name}'"
        audit_logs = await role.guild.audit_logs(limit=1, action=disnake.AuditLogAction.role_create).flatten()
        user = audit_logs[0].user if audit_logs else None
        await self.log_action(action, user, role.guild.system_channel, "role_change_log")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        try:
            action = f"Роль '{role.name}' была удалена на сервере '{role.guild.name}'"
            audit_logs = await role.guild.audit_logs(limit=1, action=disnake.AuditLogAction.role_delete).flatten()
            user = audit_logs[0].user if audit_logs else None
            await self.log_action(action, user, role.guild.system_channel, "role_change_log")
        except Exception as e:
            print(f"Произошла ошибка в on_guild_role_delete: {e}")

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        action = f"Роль '{before.name}' была изменена на '{after.name}' на сервере '{before.guild.name}'"
        audit_logs = await before.guild.audit_logs(limit=1, action=disnake.AuditLogAction.role_update).flatten()
        user = audit_logs[0].user if audit_logs else None
        await self.log_action(action, user, before.guild.system_channel, "role_change_log")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        try:
            added_roles = [role for role in after.roles if role not in before.roles]
            if added_roles:
                for role in added_roles:
                    action = f"Роль '{role.name}' была добавлена пользователю '{after.name}'"
                    audit_logs = await after.guild.audit_logs(limit=1, action=disnake.AuditLogAction.member_role_update).flatten()
                    executor = audit_logs[0].user if audit_logs else None
                    await self.log_action(action, executor, after.guild.system_channel, "rolemem_change_log")

            removed_roles = [role for role in before.roles if role not in after.roles]
            if removed_roles:
                for role in removed_roles:
                    action = f"Роль '{role.name}' была удалена у пользователя '{after.name}'"
                    audit_logs = await after.guild.audit_logs(limit=1, action=disnake.AuditLogAction.member_role_update).flatten()
                    executor = audit_logs[0].user if audit_logs else None
                    await self.log_action(action, executor, after.guild.system_channel, "rolemem_change_log")
        except Exception as e:
            print(f"Произошла ошибка в on_member_update: {e}")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        # Создание embed-сообщения для уведомления о том, что бот был выгнан с сервера
        embed = disnake.Embed(
            title="Бот выгнан с сервера",
            description=f"Бот был выгнан с сервера **{guild.name}**",
            color=disnake.Color.red()  # Красный цвет для уведомления о выгоне
        )
        embed.add_field(name="ID сервера", value=guild.id, inline=False)

        await self.send_webhook("guild_log", embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Создание embed-сообщения для уведомления о том, что бот был добавлен на сервер
        embed = disnake.Embed(
            title="Бот добавлен на сервер",
            description=f"Бот был добавлен на сервер **{guild.name}**",
            color=disnake.Color.green()  # Зеленый цвет для уведомления о добавлении
        )
        embed.add_field(name="ID сервера", value=guild.id, inline=False)

        await self.send_webhook("guild_log", embed=embed)

    # Логи редактирования каналов ----------
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        action = f"Канал '{channel.name}' был создан на сервере '{channel.guild.name}'"
        audit_logs = await channel.guild.audit_logs(limit=1, action=disnake.AuditLogAction.channel_create).flatten()
        user = audit_logs[0].user if audit_logs else None
        await self.log_action(action, user, channel.guild.system_channel, "channel_change_log")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        action = f"Канал '{channel.name}' был удален на сервере '{channel.guild.name}'"
        audit_logs = await channel.guild.audit_logs(limit=1, action=disnake.AuditLogAction.channel_delete).flatten()
        user = audit_logs[0].user if audit_logs else None
        await self.log_action(action, user, channel.guild.system_channel, "channel_change_log")

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        action = f"Канал '{before.name}' был изменен на '{after.name}' на сервере '{before.guild.name}'"
        audit_logs = await before.guild.audit_logs(limit=1, action=disnake.AuditLogAction.channel_update).flatten()
        user = audit_logs[0].user if audit_logs else None
        await self.log_action(action, user, before.guild.system_channel, "channel_change_log")

    # Логи редактирования сервера ----------
    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        action = f"Сервер '{before.name}' был изменен на '{after.name}'"
        audit_logs = await before.audit_logs(limit=1, action=disnake.AuditLogAction.guild_update).flatten()
        user = audit_logs[0].user if audit_logs else None
        await self.log_action(action, user, before.system_channel, "server_change_log")

    # Логи редактирования эмодзи, стикеров ----------
    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        added_emojis = [emoji for emoji in after if emoji not in before]
        for emoji in added_emojis:
            action = f"Эмодзи '{emoji.name}' был добавлен на сервере '{guild.name}'"
            audit_logs = await guild.audit_logs(limit=1, action=disnake.AuditLogAction.emoji_create).flatten()
            executor = audit_logs[0].user if audit_logs else None
            await self.log_action(action, executor, guild.system_channel, "servermem_change_log")

        removed_emojis = [emoji for emoji in before if emoji not in after]
        for emoji in removed_emojis:
            action = f"Эмодзи '{emoji.name}' был удален на сервере '{guild.name}'"
            audit_logs = await guild.audit_logs(limit=1, action=disnake.AuditLogAction.emoji_delete).flatten()
            executor = audit_logs[0].user if audit_logs else None
            await self.log_action(action, executor, guild.system_channel, "servermem_change_log")

    @commands.Cog.listener()
    async def on_sticker_create(self, sticker):
        action = f"Стикер '{sticker.name}' был добавлен на сервере '{sticker.guild.name}'"
        audit_logs = await sticker.guild.audit_logs(limit=1, action=disnake.AuditLogAction.sticker_create).flatten()
        executor = audit_logs[0].user if audit_logs else None
        await self.log_action(action, executor, sticker.guild.system_channel, "servermem_change_log")

    @commands.Cog.listener()
    async def on_sticker_delete(self, sticker):
        action = f"Стикер '{sticker.name}' был удален на сервере '{sticker.guild.name}'"
        audit_logs = await sticker.guild.audit_logs(limit=1, action=disnake.AuditLogAction.sticker_delete).flatten()
        executor = audit_logs[0].user if audit_logs else None
        await self.log_action(action, executor, sticker.guild.system_channel, "servermem_change_log")

    # Логи банов ----------
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        action = f"Пользователь '{user.name}' был забанен на сервере '{guild.name}'"
        audit_logs = await guild.audit_logs(limit=1, action=disnake.AuditLogAction.ban).flatten()
        executor = audit_logs[0].user if audit_logs else None
        await self.log_action(action, executor, guild.system_channel, "member_kek_log")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        action = f"Пользователь '{user.name}' был разбанен на сервере '{guild.name}'"
        audit_logs = await guild.audit_logs(limit=1, action=disnake.AuditLogAction.unban).flatten()
        executor = audit_logs[0].user if audit_logs else None
        await self.log_action(action, executor, guild.system_channel, "member_kek_log")

def setup(bot):
    bot.add_cog(Logging(bot))
    print(f"Подключение модуля Logging...")