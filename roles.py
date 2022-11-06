from time import sleep
import discord, re, random
from discord.ext import commands

EXCLUDE_ROLES = [484805623209525258]

EVE_ROLES = [
["880572127823159366", ""],
["880572192872611871", ""],
["885936958394748950", ""]
]
LGBT_ROLES = [
["1007573574082642011", ""],
["1007573880728199188", ""],
["1007573890198949920", ""],
["1007573993135558679", ""],
["1007575326227972209", ""],
["1007623293811032157", ""],
["1007623250118987796", ""],
["1007573999699628072", ""],
["1007574163302658081", ""],
["1007574166242861117", ""]
]
TOPIC_ROLES = [
["1037691564954238996", "Grants access to the neurodivergent chat channel"],
["972970423744610374", ""],
["972970633174614058", ""],
["972970544670584852", ""]
]
GUILDS = ["484805623209525258"]

class Roles(commands.Cog):
    def __init__(self, bot, guilds):
        self.bot = bot
        global GUILDS
        GUILDS = guilds

    @commands.slash_command(description="Add/remove roles from yourself. Tag them to share things, find others to play games with, etc", guild_ids=GUILDS)
    async def roles(self, ctx):
        print(f"[roles] Responding to {ctx.user}")

        roles = ctx.user.roles
        embed, view = self.GetRoleEmbed(ctx, roles, None)
        await ctx.respond(ephemeral=True, embed=embed, view=view)

    def GetRoleEmbed(self, ctx, roles, last_update):
        rolelist = ""
        for r in reversed(roles):
            if r.id not in EXCLUDE_ROLES:
                rolelist += f"<@&{r.id}> "

        view = self.RoleView(ctx, last_update, self)
        embed = discord.Embed(color=0x299aff, description=f"*Hello <@{ctx.user.id}>, your current roles are:\n{rolelist}\n\nUse the menus below to add or remove roles.*")

        return embed, view

    class RoleView(discord.ui.View):
        def __init__(self, ctx, last_update, cog):
            super().__init__()

            self.add_item(cog.RoleDropdown(ctx, "EVE Online roles", EVE_ROLES, last_update, cog))
            self.add_item(cog.RoleDropdown(ctx, "🏳️‍🌈 LGBT roles - Grant access to the #🌈lgbt channel", LGBT_ROLES, last_update, cog))
            self.add_item(cog.RoleDropdown(ctx, "Misc/Topic roles", TOPIC_ROLES, last_update, cog))

    class RoleDropdown(discord.ui.Select):
        def __init__(self, ctx, placeholder, roles, last_update, cog):
            self.ctx = ctx
            self.cog = cog
            options = []

            for r in roles:
                role = ctx.guild.get_role(int(r[0]))

                description = r[1]
                if role in ctx.user.roles or (last_update and last_update[0] == 1 and role is last_update[1]):
                    description="You already have this role. Click to remove it"
                if last_update and last_update[0] == 0 and role is last_update[1]:
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

                    last_update = [0, role]
                    roles.remove(role)

                    await interaction.user.remove_roles(role)
                else:
                    print(f"[roles] Adding roles to {interaction.user}")

                    last_update = [1, role]
                    roles.insert(0, role)

                    await interaction.user.add_roles(role)

            embed, view = self.cog.GetRoleEmbed(self.ctx, roles, last_update)
            await interaction.response.edit_message(embed=embed, view=view)
