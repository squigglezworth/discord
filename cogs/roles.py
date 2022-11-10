import discord, re, random
from discord.ext import commands

class Roles(commands.Cog):
    def __init__(self, bot, exclude, menus, guilds = None):
        self.bot = bot
        self.exclude = exclude
        # Add @everyone to the exclude list
        self.exclude.append(484805623209525258)
        self.menus = menus

        print(f"[roles] Registering" + (f" on {len(guilds)} guilds" if guilds else " globally"))

    @commands.slash_command()
    async def roles(self, ctx):
        """
        Add/remove roles from yourself. Tag them to share things, find others to play games with, etc
        """
        print(f"[roles] Responding to {ctx.user}")

        roles = ctx.user.roles
        embed, view = self.GetRoleEmbed(ctx, roles, None)

        await ctx.respond(ephemeral=True, embed=embed, view=view)

    def GetRoleEmbed(self, ctx, roles, LastUpdate):
        RoleList = ""
        for r in reversed(roles):
            if r.id not in self.exclude:
                RoleList += f"<@&{r.id}> "

        view = self.RoleView(ctx, LastUpdate, self)
        embed = discord.Embed(color=0x299aff, description=f"*Hello <@{ctx.user.id}>, your current roles are:\n{RoleList}\n\nUse the menus below to add or remove roles.*")

        return embed, view

    class RoleView(discord.ui.View):
        def __init__(self, ctx, LastUpdate, cog):
            super().__init__()

            for m in cog.menus:
                self.add_item(cog.RoleDropdown(ctx, m["placeholder"], m["roles"], LastUpdate, cog))

    class RoleDropdown(discord.ui.Select):
        def __init__(self, ctx, placeholder, roles, LastUpdate, cog):
            self.ctx = ctx
            self.cog = cog
            options = []

            for r in roles:
                role = ctx.guild.get_role(r[0])

                description = r[1]
                if role in ctx.user.roles or (LastUpdate and LastUpdate[0] == 1 and role is LastUpdate[1]):
                    description="You already have this role. Click to remove it"
                if LastUpdate and LastUpdate[0] == 0 and role is LastUpdate[1]:
                    description=r[1]

                options += [discord.SelectOption(
                    label=role.name,
                    description=description,
                    value=str(role.id),
                )]

            super().__init__(
                    placeholder=placeholder,
                	options=options,
                    min_values=1,
           	)

        async def callback(self, interaction: discord.Interaction):
            roles = interaction.user.roles

            for r in self.values:
                role = interaction.guild.get_role(int(r))
                if role in interaction.user.roles:
                    print(f"[roles] Removing roles from {interaction.user}")

                    LastUpdate = [0, role]
                    roles.remove(role)

                    await interaction.user.remove_roles(role)
                else:
                    print(f"[roles] Adding roles to {interaction.user}")

                    LastUpdate = [1, role]
                    roles.insert(0, role)

                    await interaction.user.add_roles(role)

            embed, view = self.cog.GetRoleEmbed(self.ctx, roles, LastUpdate)

            await interaction.response.edit_message(embed=embed, view=view)
