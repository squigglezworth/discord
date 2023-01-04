import discord
import re
import random
import logging
from random import shuffle
from discord.ext import commands


class Roles:
    def __init__(self, bot, settings):
        """
        Register commands according to the provided settings
        """
        self.logger = bot.logger
        self.settings = settings

        for c in settings:
            bot.logger.info(f"Registering /{c}")

            command = discord.SlashCommand(
                self.CommandCallback,
                name=c,
                description=settings[c]["description"],
            )

            bot.add_application_command(command)

    async def CommandCallback(self, ctx):
        """
        Callback for commands
        """
        self.ctx = ctx
        embed, view = self.Message()

        await ctx.respond(ephemeral=True, embed=embed, view=view)

    def Message(self, ctx=None, menu=None, user_roles=None, updates=None, extras=None):
        """
        Assemble the message - including an embed and the View
        """
        if ctx:
            self.ctx = ctx
        else:
            ctx = self.ctx

        if not menu:
            menu = self.settings[str(ctx.command)]

        embed_data = {"ctx": ctx, "RolesList": "", "ShortRolesList": "", "MenuRoles": ""}
        if not user_roles:
            user_roles = ctx.user.roles

        # Assemble a list of all roles for this menu
        roles = []
        for m in menu["dropdowns"]:
            for r in m["roles"]:
                roles += [r[0]]
                embed_data["MenuRoles"] += f"<@&{r[0]}>  "

        self.menu_roles = roles

        # Here we build some strings that can be used in the embed:
        # RolesList is a list of all the user's roles, save @everyone and anything in 'exclude''
        # ShortRolesList is a list of roles the user has that are also present in the menu
        # MenuRoles (assembled above) is a list of roles in this menu
        for r in reversed(user_roles):
            if r.id not in menu["exclude"] + [484805623209525258]:
                embed_data["RolesList"] += f"<@&{r.id}> "
            if r.id in roles:
                embed_data["ShortRolesList"] += f"<@&{r.id}> "
        if not embed_data["ShortRolesList"]:
            embed_data["ShortRolesList"] = "empty!"

        # Prepare & return the view and embed
        view = self.View(self, menu, updates, extras)

        embed = discord.Embed(color=0x299AFF, description=menu["embed"].format(**embed_data))

        if not view.children:
            embed.description = "Uh oh, something's went wrong. Please contact your admin!"

        return embed, view

    class View(discord.ui.View):
        def __init__(self, cog, menu, updates=None, extras=None):
            """
            The View holds dropdowns, buttons, etc
            """
            super().__init__()

            self.cog = cog
            self.menu = menu
            self.updates = updates
            self.extras = extras

            for dropdown in menu["dropdowns"]:
                try:
                    self.add_item(self.Dropdown(dropdown, self, cog))
                except:
                    cog.logger.warning(f"{cog.ctx.command} - Couldn't build dropdown!")

            if self.children:
                self.add_item(self.ClearButton(self, cog))

        class Dropdown(discord.ui.Select):
            def __init__(self, settings, view, cog):
                """
                Assemble a dropdown according to the provided settings
                """
                self.settings = settings
                self.View = view
                self.cog = cog
                options = []

                if settings["randomize"]:
                    shuffle(settings["roles"])

                for r in settings["roles"]:
                    role = cog.ctx.guild.get_role(r[0])

                    if not role:
                        cog.logger.warning(f"{cog.ctx.command} - Role does not exist on server - {role}")
                        continue

                    update = None
                    description = r[1]
                    # Check if the user added or removed this role last time
                    if view.updates and role in [u[1] for u in view.updates]:
                        update = list(filter(lambda u: u[1] == role, view.updates))[0][0]
                    # Check if the user already has this role, or if they added it with the last interaction
                    if update == 1 or role in cog.ctx.user.roles:
                        description = "You already have this role; click to remove it"
                    if update == 0:
                        description = r[1]

                    option = discord.SelectOption(label=role.name, description=description, value=str(role.id))

                    if r[2]:
                        option.emoji = r[2]

                    options += [option]

                if options:
                    super().__init__(
                        placeholder=settings["placeholder"],
                        options=options,
                        min_values=1,
                    )

            async def callback(self, interaction):
                """
                Callback for dropdown menus
                """
                user_roles = interaction.user.roles
                updates = []

                for r in self.values:
                    role = interaction.guild.get_role(int(r))

                    if role in user_roles:
                        # If the user already has the role, remove it
                        self.cog.logger.info(f"{self.cog.ctx.command} - Removing roles from {interaction.user} - {role}")

                        updates += [0, role]
                        user_roles.remove(role)
                        await interaction.user.remove_roles(role)
                    else:
                        # If the user doesn't have the role, add it
                        if self.View.menu["max_one"]:
                            # But first, if max_one is set, remove any other roles the user has from this menu
                            self.cog.logger.info(f"{self.cog.ctx.command} - max_one specified; removing all roles...")

                            roles = self.cog.menu_roles

                            # Add all the roles we're about to replace to the updates array
                            for r in filter(
                                lambda r: r.id in roles,
                                user_roles,
                            ):
                                updates += [0, r]
                            # Filter out the roles in this menu from the user's roles
                            # This list will be used to update the user
                            user_roles = list(
                                filter(
                                    lambda r: r.id not in roles,
                                    interaction.user.roles,
                                )
                            )
                            await interaction.user.edit(roles=user_roles)

                        self.cog.logger.info(f"{self.cog.ctx.command} - Adding roles to {interaction.user} - {role}")

                        # Prepare some info for refresh
                        updates += [1, role]
                        user_roles.insert(0, role)
                        # Let's finally add the role to the user
                        await interaction.user.add_roles(role)

                embed, view = self.cog.Message(menu=self.View.menu, user_roles=user_roles, updates=[updates], extras=self.View.extras)

                if self.view.extras:
                    for v in self.View.extras:
                        view.add_item(v)

                await interaction.response.edit_message(embed=embed, view=view)

        class ClearButton(discord.ui.Button):
            def __init__(self, view, cog):
                """
                Adds a button to clear all roles
                """
                self.View = view
                self.cog = cog

                super().__init__(label="Clear all roles", style=discord.ButtonStyle.danger)

            async def callback(self, interaction):
                """
                Callback for the clear button
                """
                self.cog.logger.info(f"{cog.ctx.command} - Clearing all roles from {interaction.user}")

                updates = []
                for r in filter(lambda r: r.id in self.cog.menu_roles, interaction.user.roles):
                    updates.append([0, r])

                user_roles = list(filter(lambda r: r.id not in self.cog.menu_roles, interaction.user.roles))

                await interaction.user.edit(roles=user_roles)
                embed, view = self.cog.Message(menu=self.View.menu, user_roles=user_roles, updates=updates, extras=self.View.extras)

                if self.view.extras:
                    for v in self.view.extras:
                        view.add_item(v)

                await interaction.response.edit_message(embed=embed, view=view)
