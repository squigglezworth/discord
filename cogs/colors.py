import discord, re, random, logging
from discord.ext import commands

logger = logging.getLogger("bot.colors")


class Colors(commands.Cog):
    def __init__(self, bot, prefix, guilds=None):
        self.bot = bot
        self.prefix = prefix

        logger.info(f"Registering /colors" + (f" on {len(guilds)} guilds" if guilds else " globally"))

        command = discord.SlashCommand(
            self.CommandCallback,
            name="colors",
            description="Give your messages a bit of flair with a fancy color role!",
        )

        bot.add_application_command(command)

    async def CommandCallback(self, ctx):
        embed, view = self.Message(ctx)

        await ctx.respond(ephemeral=True, embed=embed, view=view)

    def Message(self, ctx, LastUpdate=None, ExtraViews=None):
        RoleList = ""
        UserColor = ""

        # Retrieve a list of all color roles
        roles = ctx.guild.roles
        pattern = re.compile(f"{re.escape(self.prefix)}.*")
        ColorRoles = list(filter(lambda x: pattern.match(x.name), roles))
        random.shuffle(ColorRoles)

        for r in ColorRoles:
            RoleList += f"<@&{r.id}>  "

        UserColor = "empty!"
        if LastUpdate:
            UserColor = f"<@&{LastUpdate[1].id}>" if LastUpdate[0] == 1 else f"empty!"
        else:
            for r in ctx.user.roles:
                pattern = re.compile("\[C\].*")
                if pattern.match(r.name):
                    UserColor = f"<@&{r.id}>"

        view = self.View(ctx, self, ColorRoles, ExtraViews)
        embed = discord.Embed(
            color=0x299AFF,
            description=f"*Hello <@{ctx.user.id}>, your current color is {UserColor}\n\nAvailable colors are: {RoleList}*",
        )

        return embed, view

    class View(discord.ui.View):
        def __init__(self, ctx, cog, ColorRoles, ExtraViews):
            super().__init__()

            self.add_item(cog.Dropdown(ctx, ColorRoles, cog, ExtraViews))
            self.add_item(cog.ClearButton(ctx, ColorRoles, cog, ExtraViews))

    class Dropdown(discord.ui.Select):
        def __init__(self, ctx, ColorRoles, cog, ExtraViews=None):
            self.ctx = ctx
            self.colors = ColorRoles
            self.cog = cog
            self.ExtraViews = ExtraViews
            options = []

            for r in ColorRoles:
                options += [discord.SelectOption(label=r.name.removeprefix(cog.prefix), value=str(r.id))]

            super().__init__(
                placeholder="🌈 Select a color!",
                options=options,
                min_values=1,
            )

        async def callback(self, interaction: discord.Interaction):
            pattern = re.compile("\[C\].*")

            for r in interaction.user.roles:
                if pattern.match(r.name):
                    logger.info(f"Removing color from {interaction.user}")

                    await interaction.user.remove_roles(r)
                    LastUpdate = [0, r]

            for r in self.values:
                role = interaction.guild.get_role(int(r))

                if role in interaction.user.roles:
                    logger.info(f"Removing color from {interaction.user}")

                    await interaction.user.remove_roles(role)
                    LastUpdate = [0, role]
                else:
                    logger.info(f"Adding color to {interaction.user}")

                    await interaction.user.add_roles(role)
                    LastUpdate = [1, role]

            embed, view = self.cog.Message(self.ctx, LastUpdate, ExtraViews=self.ExtraViews)

            if self.ExtraViews:
                for v in self.ExtraViews:
                    view.add_item(v)

            await interaction.response.edit_message(embed=embed, view=view)

    class ClearButton(discord.ui.Button):
        def __init__(self, ctx, roles, cog, extras):
            self.ctx = ctx
            self.roles = roles
            self.cog = cog
            self.extras = extras

            super().__init__(label="Clear color role", style=discord.ButtonStyle.danger)

        async def callback(self, interaction):
            # Add all the roles we're about to remove to the updates array
            updates = []
            for f in filter(lambda r: r.id in [r.id for r in self.roles], interaction.user.roles):
                updates.append([0, f])

            user_roles = list(filter(lambda r: r.id not in [r.id for r in self.roles], interaction.user.roles))
            await interaction.user.edit(roles=user_roles)

            embed, view = self.cog.Message(self.ctx, updates, self.extras)

            if self.extras:
                for v in self.extras:
                    view.add_item(v)

            await interaction.response.edit_message(embed=embed, view=view)
