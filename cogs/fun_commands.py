from imports import *

# Функция для загрузки конфигурации
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Модуль {self.__class__.__name__} подключен.")

    @commands.slash_command(description="Команды для развлечения.\n\nИмеет подкоманды")
    async def fun(self, interaction: disnake.ApplicationCommandInteraction):
        pass  # Это будет родительская команда, которая ничего не делает

# Шлеп --------------------------------------------------------------------------------------------------------------------------
    @fun.sub_command(description="Шлепнуть по попе")
    async def slap(self, interaction: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        # Если пользователь не указан, используем автора команды
        if user is None:
            user = interaction.user
        roles = interaction.user.roles
        female_role_id = self.config["roles"]["female"]["role_id"]
        male_role_id = self.config["roles"]["male"]["role_id"]
        has_female_role = any(role.id == female_role_id for role in roles)
        has_male_role = any(role.id == male_role_id for role in roles)

        if not has_female_role and not has_male_role:
            await interaction.send("Ты по-моему что-то перепутал, ты либо не на том сервере, либо определи себя, мужчина ты или женщина, отказано в выполнении команды.")
            return

        if has_female_role:
            action_description = "ударила"
        else:
            action_description = "ударил"

        if user == interaction.user:
            description = f"{interaction.user.mention} {action_description} себя по попе!"
            # Список гифок для удара по себе
            gif_list = [
                "https://media.tenor.com/AEWh7M4iBEYAAAAM/spanking-spank.gif",
                "https://media.tenor.com/MWOs_f48n2cAAAAM/slap-my-ass-godku.gif",
                "https://media.tenor.com/L94kvBQ5BH8AAAAM/pingu-slap.gif"
            ]
        else:
            description = f"{interaction.user.mention} {action_description} по попе {user.mention}!"
            # Список гифок для удара по другому пользователю
            gif_list = [
                "https://media.tenor.com/XW_ymVr5I6sAAAAM/slap-butt.gif", 
                "https://media.tenor.com/AiLrNJMakwIAAAAM/mochi-bunny.gif",
                "https://media.tenor.com/v20N16whtvoAAAAM/butt-slap-booty-slap.gif"
            ]

        # Создаем эмбед
        embed = disnake.Embed(
            description=description,
            color=disnake.Color.from_rgb(43, 45, 49)  # Используем стандартный цвет
        )
        
        # Выбираем случайную гифку из списка
        random_gif = random.choice(gif_list)
        embed.set_image(url=random_gif)

        # Устанавливаем футер
        embed.set_footer(text="Отшлепан как следует")

        # Отправляем эмбед
        await interaction.send(embed=embed)

# Обнять --------------------------------------------------------------------------------------------------------------------------
    @fun.sub_command(description="Обнять")
    async def hug(self, interaction: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        if user is None:
            user = interaction.user
        roles = interaction.user.roles
        female_role_id = self.config["roles"]["female"]["role_id"]
        male_role_id = self.config["roles"]["male"]["role_id"]
        has_female_role = any(role.id == female_role_id for role in roles)
        has_male_role = any(role.id == male_role_id for role in roles)

        if not has_female_role and not has_male_role:
            await interaction.send("Ты по-моему что-то перепутал, ты либо не на том сервере, либо определи себя, мужчина ты или женщина, отказано в выполнении команды.")
            return
            
        if has_female_role:
            action_description = "обняла"
        else:
            action_description = "обнял"
        if user == interaction.user:
            description = f"{interaction.user.mention} {action_description} себя.."
            # по себе
            gif_list = [
                "https://media.tenor.com/kkW-x5TKP-YAAAAM/seal-hug.gif",
                "https://media.tenor.com/kzFMcr-dmyIAAAAM/espa%C3%B1a-2021.gif",
                "https://media.tenor.com/oZOE7Xrxz2UAAAAM/graceand-frankie-hug.gif"
            ]
        else:
            description = f"{interaction.user.mention} крепко {action_description} {user.mention}!"
            # по другому пользователю
            gif_list = [
                "https://media.tenor.com/yMjbC5MEv5UAAAAM/hug-squeeze.gif", 
                "https://media.tenor.com/aLF8700Drh0AAAAM/eszan-hugging-couple.gif",
                "https://media.tenor.com/9lgQMsG7WEAAAAAM/couple-couple-hug.gif"
            ]
        embed = disnake.Embed(
            description=description,
            color=disnake.Color.from_rgb(43, 45, 49)
        )
        random_gif = random.choice(gif_list)
        embed.set_image(url=random_gif)
        embed.set_footer(text="мммм, обнимашкиии <3")
        await interaction.send(embed=embed)

# Поцеловать --------------------------------------------------------------------------------------------------------------------------
    @fun.sub_command(description="Поцеловать")
    async def kiss(self, interaction: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        if user is None:
            user = interaction.user
        roles = interaction.user.roles
        female_role_id = self.config["roles"]["female"]["role_id"]
        male_role_id = self.config["roles"]["male"]["role_id"]
        has_female_role = any(role.id == female_role_id for role in roles)
        has_male_role = any(role.id == male_role_id for role in roles)

        if not has_female_role and not has_male_role:
            await interaction.send("Ты по-моему что-то перепутал, ты либо не на том сервере, либо определи себя, мужчина ты или женщина, отказано в выполнении команды.")
            return
            
        if has_female_role:
            action_description = "поцеловала"
        else:
            action_description = "поцеловал"
        if user == interaction.user:
            description = f"{interaction.user.mention} {action_description}.... себя?"
            # по себе
            gif_list = [
                "https://media.tenor.com/0-ZcXybzvIgAAAAM/edoardo-esposito-valerio-mazzei.gif",
                "https://media.tenor.com/Z6beFKdZ9RYAAAAM/kissing-myself-dj-hunts.gif",
                "https://media.tenor.com/B82nmzIDizcAAAAM/self-love-kiss.gif"
            ]
        else:
            description = f"{interaction.user.mention} романтично {action_description} {user.mention}!"
            # по другому пользователю
            gif_list = [
                "https://media.tenor.com/nnCcQiV6H0gAAAAM/romantic-kiss-phantom-of-the-opera.gif", 
                "https://media.tenor.com/lXoRYgg3B8QAAAAM/kallis.gif",
                "https://media.tenor.com/wXfUjrXrdY4AAAAM/h%C3%B4n.gif"
            ]
        embed = disnake.Embed(
            description=description,
            color=disnake.Color.from_rgb(43, 45, 49)
        )
        random_gif = random.choice(gif_list)
        embed.set_image(url=random_gif)
        embed.set_footer(text="поцелуйчики, как мило <3")
        await interaction.send(embed=embed)

# Укусить --------------------------------------------------------------------------------------------------------------------------
    @fun.sub_command(description="Укусить")
    async def bite(self, interaction: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        if user is None:
            user = interaction.user
        roles = interaction.user.roles
        female_role_id = self.config["roles"]["female"]["role_id"]
        male_role_id = self.config["roles"]["male"]["role_id"]
        has_female_role = any(role.id == female_role_id for role in roles)
        has_male_role = any(role.id == male_role_id for role in roles)

        if not has_female_role and not has_male_role:
            await interaction.send("Ты по-моему что-то перепутал, ты либо не на том сервере, либо определи себя, мужчина ты или женщина, отказано в выполнении команды.")
            return
            
        if has_female_role:
            action_description = "укусила"
        else:
            action_description = "укусил"
        if user == interaction.user:
            description = f"{interaction.user.mention} {action_description} себя"
            # по себе
            gif_list = [
                "https://media.tenor.com/azy9i6rPInQAAAAM/omg-leonardo-di-caprio.gif",
                "https://media.tenor.com/yzoxPfcq_4kAAAAM/oh-my-god-so-good.gif",
                "https://media.tenor.com/VlxVsUxP87kAAAAM/wooyoung-holding-back-wooyoung-shhh.gif"
            ]
        else:
            description = f"{interaction.user.mention} {action_description} {user.mention}!"
            # по другому пользователю
            gif_list = [
                "https://media.tenor.com/qpB8JyiwDNQAAAAM/anime-anime-hug.gif", 
                "https://media.tenor.com/HuE9vf7guRoAAAAj/lily-and-marigold.gif",
                "https://media.tenor.com/XvnWPFz_fLUAAAAM/butt-sandwich.gif"
            ]
        embed = disnake.Embed(
            description=description,
            color=disnake.Color.from_rgb(43, 45, 49)
        )
        random_gif = random.choice(gif_list)
        embed.set_image(url=random_gif)
        embed.set_footer(text="кусаться это одновременно и классно и больно...")
        await interaction.send(embed=embed)

# Тыкнуть --------------------------------------------------------------------------------------------------------------------------
    @fun.sub_command(description="Тыкнуть")
    async def poke(self, interaction: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        if user is None:
            user = interaction.user
        roles = interaction.user.roles
        female_role_id = self.config["roles"]["female"]["role_id"]
        male_role_id = self.config["roles"]["male"]["role_id"]
        has_female_role = any(role.id == female_role_id for role in roles)
        has_male_role = any(role.id == male_role_id for role in roles)

        if not has_female_role and not has_male_role:
            await interaction.send("Ты по-моему что-то перепутал, ты либо не на том сервере, либо определи себя, мужчина ты или женщина, отказано в выполнении команды.")
            return
            
        if has_female_role:
            action_description = "тыкнула"
        else:
            action_description = "тыкнул"
        if user == interaction.user:
            description = f"{interaction.user.mention} {action_description} в себя, главное не проткнуть"
            # по себе
            gif_list = [
                "https://media.tenor.com/Zd82uOH6oKsAAAAM/andteam-andteam-ej.gif",
                "https://media.tenor.com/cdJkGakKAL8AAAAM/the-boyz-tbz.gif",
                "https://media.tenor.com/6TpszrCo62UAAAAM/kevin-james-poke-eyes.gif"
            ]
        else:
            description = f"{interaction.user.mention} {action_description} {user.mention}, главное не проткнуть!"
            # по другому пользователю
            gif_list = [
                "https://media.tenor.com/aBgO4yu5E-cAAAAM/three-stooges.gif", 
                "https://media.tenor.com/Qgym_eq04DMAAAAM/smap-inagaki-goro.gif",
                "https://media.tenor.com/_1clA0nw-dgAAAAM/bunnies-poke-cheek.gif"
            ]
        embed = disnake.Embed(
            description=description,
            color=disnake.Color.from_rgb(43, 45, 49)
        )
        random_gif = random.choice(gif_list)
        embed.set_image(url=random_gif)
        embed.set_footer(text="тыкать в людей не хорошо(")
        await interaction.send(embed=embed)

# Ударить --------------------------------------------------------------------------------------------------------------------------
    @fun.sub_command(description="Ударить")
    async def punch(self, interaction: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        if user is None:
            user = interaction.user
        roles = interaction.user.roles
        female_role_id = self.config["roles"]["female"]["role_id"]
        male_role_id = self.config["roles"]["male"]["role_id"]
        has_female_role = any(role.id == female_role_id for role in roles)
        has_male_role = any(role.id == male_role_id for role in roles)

        if not has_female_role and not has_male_role:
            await interaction.send("Ты по-моему что-то перепутал, ты либо не на том сервере, либо определи себя, мужчина ты или женщина, отказано в выполнении команды.")
            return
            
        if has_female_role:
            action_description = "ударила"
        else:
            action_description = "ударил"
        if user == interaction.user:
            description = f"{interaction.user.mention} зачем-то себя {action_description}"
            # по себе
            gif_list = [
                "https://media.tenor.com/e0gkSh1ZGa4AAAAM/momo-twice.gif",
                "https://media.tenor.com/VNWOIH7fByIAAAAM/fight-club.gif",
                "https://media.tenor.com/kHWKe62-KJoAAAAM/perry-funny.gif"
            ]
        else:
            description = f"{interaction.user.mention} красиво {action_description} {user.mention}"
            # по другому пользователю
            gif_list = [
                "https://media.tenor.com/YTVzMpGOKLwAAAAM/spy-x-family-anya-forger.gif", 
                "https://media.tenor.com/yURTsYRnGYQAAAAM/punch-in-the-face.gif",
                "https://media.tenor.com/6Cp5tiRwh-YAAAAM/meme-memes.gif"
            ]
        embed = disnake.Embed(
            description=description,
            color=disnake.Color.from_rgb(43, 45, 49)
        )
        random_gif = random.choice(gif_list)
        embed.set_image(url=random_gif)
        embed.set_footer(text="махаца будешь?")
        await interaction.send(embed=embed)

# Секс --------------------------------------------------------------------------------------------------------------------------
    @fun.sub_command(description="Устроить разврат")
    async def sex(self, interaction: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        if user is None:
            user = interaction.user
        roles = interaction.user.roles
        female_role_id = self.config["roles"]["female"]["role_id"]
        male_role_id = self.config["roles"]["male"]["role_id"]
        has_female_role = any(role.id == female_role_id for role in roles)
        has_male_role = any(role.id == male_role_id for role in roles)

        if not has_female_role and not has_male_role:
            await interaction.send("Ты по-моему что-то перепутал, ты либо не на том сервере, либо определи себя, мужчина ты или женщина, отказано в выполнении команды.")
            return
            
        if has_female_role:
            action_description = "занялась"
        else:
            action_description = "занялся"
        if user == interaction.user:
            description = f"{interaction.user.mention} {action_description} непристояностями"
            # по себе
            gif_list = [
                "https://media.tenor.com/EwcJLtH6Q1wAAAAj/pepe-the-frog-salami.gif",
                "https://media.tenor.com/poVXFX82K8UAAAAM/funny-wank.gif",
                "https://media.tenor.com/9KLIfpQNkX4AAAAM/masterbating-sorry.gif"
            ]
        else:
            description = f"{interaction.user.mention} {action_description} сексом с {user.mention} прям на публике..."
            # по другому пользователю
            gif_list = [
                "https://media.tenor.com/1Q7CgxMlm04AAAAM/hot-tease.gif", 
                "https://media.tenor.com/4uRxkmbUowkAAAAM/love-couple.gif",
                "https://media.tenor.com/Z70DZ55Ueq8AAAAM/make-out-make-love.gif"
            ]
        embed = disnake.Embed(
            description=description,
            color=disnake.Color.from_rgb(43, 45, 49)
        )
        random_gif = random.choice(gif_list)
        embed.set_image(url=random_gif)
        embed.set_footer(text="сексом трахаться захотелось")
        await interaction.send(embed=embed)

# Злиться --------------------------------------------------------------------------------------------------------------------------
    @fun.sub_command(description="Злыдень")
    async def angry(self, interaction: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        if user is None:
            user = interaction.user
        roles = interaction.user.roles
        if user == interaction.user:
            description = f"{interaction.user.mention} злится"
            # по себе
            gif_list = [
                "https://media.tenor.com/qPaInIyQjnQAAAAM/mad-angry.gif",
                "https://media.tenor.com/NZZzyeSeGrQAAAAM/angry-cat-sour-cat.gif",
                "https://media.tenor.com/4jTua9zpKD0AAAAM/simpson-homer-simpson.gif"
            ]
        else:
            description = f"{interaction.user.mention} злится на {user.mention}"
            # по другому пользователю
            gif_list = [
                "https://media.tenor.com/qPaInIyQjnQAAAAM/mad-angry.gif",
                "https://media.tenor.com/NZZzyeSeGrQAAAAM/angry-cat-sour-cat.gif",
                "https://media.tenor.com/4jTua9zpKD0AAAAM/simpson-homer-simpson.gif"
            ]
        embed = disnake.Embed(
            description=description,
            color=disnake.Color.from_rgb(43, 45, 49)
        )
        random_gif = random.choice(gif_list)
        embed.set_image(url=random_gif)
        embed.set_footer(text="корвалолчику?")
        await interaction.send(embed=embed)

# Танцевать --------------------------------------------------------------------------------------------------------------------------
    @fun.sub_command(description="Потанцевать")
    async def dance(self, interaction: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        if user is None:
            user = interaction.user
        roles = interaction.user.roles
        if user == interaction.user:
            description = f"{interaction.user.mention} танцует"
            # по себе
            gif_list = [
                "https://media.tenor.com/oaY8DO-f6-kAAAAM/breakdancing-shigeyuki-nakarai.gif",
                "https://media.tenor.com/0BE3mYzHl6AAAAAM/dance-happy-dance.gif",
                "https://media.tenor.com/-IGv_i2BXpAAAAAM/gefeliciteerd.gif"
            ]
        else:
            description = f"{interaction.user.mention} танцует с {user.mention}"
            # по другому пользователю
            gif_list = [
                "https://media.tenor.com/mZNM3h1YceEAAAAM/ppz-dance.gif",
                "https://media.tenor.com/VAGI8k0rrAIAAAAM/acheron-black-swan.gif",
                "https://media.tenor.com/7E6OM79aIcMAAAAM/vito-coppola-strictly-come-dancing.gif"
            ]
        embed = disnake.Embed(
            description=description,
            color=disnake.Color.from_rgb(43, 45, 49)
        )
        random_gif = random.choice(gif_list)
        embed.set_image(url=random_gif)
        embed.set_footer(text="чай, кофе, потанцуем?)")
        await interaction.send(embed=embed)

# Грустить --------------------------------------------------------------------------------------------------------------------------
    @fun.sub_command(description="Погрустить")
    async def sad(self, interaction: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        if user is None:
            user = interaction.user
        roles = interaction.user.roles
        if user == interaction.user:
            description = f"{interaction.user.mention} грустит"
            # по себе
            gif_list = [
                "https://media.tenor.com/g2Ykg_KwrhgAAAAM/sad.gif",
                "https://media.tenor.com/bN3-8qmaViQAAAAM/bubu-sad.gif",
                "https://media.tenor.com/oSKKipnYg5MAAAAM/hamsti-hamster.gif",
                "https://media.tenor.com/h-HcXapR-x8AAAAM/piyushzen.gif",
                "https://media.tenor.com/HG-U3mueAZcAAAAM/sad-sigh.gif"
            ]
        else:
            description = f"{interaction.user.mention} грустит из-за {user.mention}"
            # по другому пользователю
            gif_list = [
                "https://media.tenor.com/g2Ykg_KwrhgAAAAM/sad.gif",
                "https://media.tenor.com/bN3-8qmaViQAAAAM/bubu-sad.gif",
                "https://media.tenor.com/oSKKipnYg5MAAAAM/hamsti-hamster.gif",
                "https://media.tenor.com/h-HcXapR-x8AAAAM/piyushzen.gif",
                "https://media.tenor.com/HG-U3mueAZcAAAAM/sad-sigh.gif"
            ]
        embed = disnake.Embed(
            description=description,
            color=disnake.Color.from_rgb(43, 45, 49)
        )
        random_gif = random.choice(gif_list)
        embed.set_image(url=random_gif)
        embed.set_footer(text="грусть печать беда")
        await interaction.send(embed=embed)

# Радоваться --------------------------------------------------------------------------------------------------------------------------
    @fun.sub_command(description="Радость")
    async def happy(self, interaction: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        if user is None:
            user = interaction.user
        roles = interaction.user.roles
        if user == interaction.user:
            description = f"{interaction.user.mention} радуется"
            # по себе
            gif_list = [
                "https://media.tenor.com/4DirSqJdE1AAAAAM/happy-day-fun-day.gif",
                "https://media.tenor.com/UlsZrG1aInIAAAAM/heavenly-joy-jerkins-i-am-so-excited.gif",
                "https://media.tenor.com/xt1--BS_5mcAAAAj/dancing-mood.gif",
                "https://media.tenor.com/M2cCDtStnvYAAAAj/hasher-happy-sticker.gif"
            ]
        else:
            description = f"{interaction.user.mention} радуется благодаря {user.mention}"
            # по другому пользователю
            gif_list = [
                "https://media.tenor.com/4DirSqJdE1AAAAAM/happy-day-fun-day.gif",
                "https://media.tenor.com/UlsZrG1aInIAAAAM/heavenly-joy-jerkins-i-am-so-excited.gif",
                "https://media.tenor.com/xt1--BS_5mcAAAAj/dancing-mood.gif",
                "https://media.tenor.com/M2cCDtStnvYAAAAj/hasher-happy-sticker.gif"
            ]
        embed = disnake.Embed(
            description=description,
            color=disnake.Color.from_rgb(43, 45, 49)
        )
        random_gif = random.choice(gif_list)
        embed.set_image(url=random_gif)
        embed.set_footer(text="белая полоса в жизни пошла, завидуйте")
        await interaction.send(embed=embed)

# Смеяться --------------------------------------------------------------------------------------------------------------------------
    @fun.sub_command(description="Смех")
    async def laugh(self, interaction: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        if user is None:
            user = interaction.user
        roles = interaction.user.roles
        if user == interaction.user:
            description = f"{interaction.user.mention} смеется, хихи хаха"
            # по себе
            gif_list = [
                "https://media.tenor.com/WGdyB0HjFVIAAAAM/lmao-meme.gif",
                "https://media.tenor.com/vG5YZlIXli8AAAAM/shirleytemple-lol.gif",
                "https://media.tenor.com/5ROtQKQ_TBgAAAAM/undertale-sans.gif",
                "https://media.tenor.com/ba6u_c1Mcb0AAAAM/futurenostlgia-laughing.gif",
                "https://media.tenor.com/nIP4ElOGl90AAAAM/laughing-simon-cowell.gif",
                "https://media.tenor.com/bwT923MexkMAAAAM/j-jonah-jameson-laugh.gif"
            ]
        else:
            description = f"{interaction.user.mention} смеется над {user.mention}"
            # по другому пользователю
            gif_list = [
                "https://media.tenor.com/WGdyB0HjFVIAAAAM/lmao-meme.gif",
                "https://media.tenor.com/vG5YZlIXli8AAAAM/shirleytemple-lol.gif",
                "https://media.tenor.com/5ROtQKQ_TBgAAAAM/undertale-sans.gif",
                "https://media.tenor.com/ba6u_c1Mcb0AAAAM/futurenostlgia-laughing.gif",
                "https://media.tenor.com/nIP4ElOGl90AAAAM/laughing-simon-cowell.gif",
                "https://media.tenor.com/bwT923MexkMAAAAM/j-jonah-jameson-laugh.gif"
            ]
        embed = disnake.Embed(
            description=description,
            color=disnake.Color.from_rgb(43, 45, 49)
        )
        random_gif = random.choice(gif_list)
        embed.set_image(url=random_gif)
        embed.set_footer(text="у вас в голове только хиханьки да хаханьки")
        await interaction.send(embed=embed)

def setup(bot):
    bot.add_cog(FunCommands(bot))
