import discord, re, random
from discord.ext import commands

class Roles(commands.Cog):
    def __init__(self, bot, settings = None, guilds = None):
        # Provide the bot instance & cog settings to later methods
        self.bot = bot
        self.exclude = settings["exclude"]
        self.exclude.append(484805623209525258) # Add @everyone to the exclude list
        self.menus = settings["menus"]

        print(f"[roles] Registering" + (f" on {len(guilds)} guilds" if guilds else " globally"))

    @commands.slash_command()
    async def roles(self, ctx):
        """
        Add/remove roles from yourself. Tag them to share things, find others to play games with, etc
        """
        print(f"[roles] Responding to {ctx.user}")

        roles = ctx.user.roles
        embed, view = self.GetMessage(ctx, roles)

        await ctx.respond(ephemeral=True, embed=embed, view=view)

    def GetMessage(self, ctx, roles, LastUpdate = None):
        RoleList = ""
        # Here we build the list of the user's current roles
        for r in reversed(roles):
            if r.id not in self.exclude:
                RoleList += f"<@&{r.id}> "

        # Prepare the View. If the user has selected a role, pass it along (LastUpdate)
        view = self.RoleView(ctx, LastUpdate, self)

        # Prepare the embed with the above RoleList
        embed = discord.Embed(color=0x299aff, description=f"*Hello <@{ctx.user.id}>, your current roles are:\n{RoleList}\n\nUse the menus below to add or remove roles.*")

        return embed, view

    class RoleView(discord.ui.View):
        def __init__(self, ctx, LastUpdate, cog):
            super().__init__()

            # Assemble a dropdown menu for each list of roles (menus) defined when the cog was added to the bot
            # If the user has selected a role, pass it too
            for m in cog.menus:
                self.add_item(cog.RoleDropdown(ctx, cog, m["placeholder"], m["roles"], LastUpdate))

    class RoleDropdown(discord.ui.Select):
        def __init__(self, ctx, cog, placeholder, roles, LastUpdate = None):
            self.ctx = ctx
            self.cog = cog
            options = []

            # Start building the dropdown menu for a given list of 'roles'
            for r in roles:
                role = ctx.guild.get_role(r[0])

                # When a user already has this role - or when the user added it last time - change the description accordingly
                description = r[1]
                if role in ctx.user.roles or (LastUpdate and LastUpdate[0] == 1 and role is LastUpdate[1]):
                    description="You already have this role. Click to remove it"
                # If the user removed the role last time - and it is thus available again - reset the description
                if LastUpdate and LastUpdate[0] == 0 and role is LastUpdate[1]:
                    description=r[1]
                # The above checks are necessary due to an outdated user instance - unsure how to retrieve an updated one

                # Add each role to the list of options
                options += [discord.SelectOption(
                    label=role.name,
                    description=description,
                    value=str(role.id),
                )]

            # Assemble & return the dropdown menu
            super().__init__(
                    placeholder=placeholder,
                	options=options,
                    min_values=1,
           	)

        async def callback(self, interaction: discord.Interaction):
            """
            Respond to a user selecting a role from a menu
            """

            for r in self.values:
                # Get the role the user has selected
                role = interaction.guild.get_role(int(r))
                # Remove it if they already have it
                if role in interaction.user.roles:
                    print(f"[roles] Removing roles from {interaction.user}")

                    # Prepare info for updating the message
                    # deleted, role
                    LastUpdate = [0, role]
                    # Add/remove it from the list of user's current roles, which will be displayed when the message is updated
                    roles.remove(role)

                    await interaction.user.remove_roles(role)
                else:
                    print(f"[roles] Adding roles to {interaction.user}")

                    # Prepare info for updating the message
                    # added, role
                    LastUpdate = [1, role]
                    # Add/remove it from the list of user's current roles, which will be displayed when the message is updated
                    roles.insert(0, role)

                    await interaction.user.add_roles(role)

            # Retrieve the message embed & view
            # The embed contains a list of the user's current roles
            # The view contains the dropdown menus
            embed, view = self.cog.GetMessage(self.ctx, roles, LastUpdate)

            # Update the existing message with the embed & view
            await interaction.response.edit_message(embed=embed, view=view)
