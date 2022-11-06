from time import sleep
import discord, re, random
from discord.ext import commands

GUILDS = ["484805623209525258"]
class Colors(commands.Cog):
    def __init__(self, ctx, guilds):
        self.ctx = ctx
        global GUILDS
        GUILDS = guilds

    @commands.slash_command(description="Give your messages a flair of color with a fancy color role!", guild_ids=GUILDS)
    async def colors(self, ctx):
        print(f"[colors] Responding to {ctx.user}")

        roles = await ctx.guild.fetch_roles()
        pattern = re.compile("\[C\].*")
        colorRoles = list(filter(lambda x: pattern.match(x.name), roles))
        embed, view = self.GetColorEmbed(ctx, colorRoles)

        await ctx.respond(ephemeral=True, embed=embed, view=view)

    def GetColorEmbed(self, ctx, colorRoles, last_update = None):
        rolelist = ""
        userColor = ""

        for r in ctx.user.roles:
            pattern = re.compile("\[C\].*")
            if pattern.match(r.name):
                userColor = f"<@&{r.id}>"
            if last_update:
                userColor = f"<@&{last_update.id}>"

        random.shuffle(colorRoles)

        for c in colorRoles:
            rolelist += f"<@&{c.id}>  "

        view = self.ColorView(ctx, colorRoles, self)
        embed = discord.Embed(color=0x299aff, description=f"*Hello <@{ctx.user.id}>, your current color is {userColor}\n\nAvailable colors are: {rolelist}*")

        return embed, view

    class ColorView(discord.ui.View):
        def __init__(self, ctx, colors, cog):
            super().__init__()

            self.add_item(cog.ColorDropdown(ctx, colors, cog))

    class ColorDropdown(discord.ui.Select):
        def __init__(self, ctx, colorRoles, cog):
            self.ctx = ctx
            self.colors = colorRoles
            self.cog = cog
            options = []

            for c in colorRoles:
                options += [discord.SelectOption(
                    label = c.name,
                    value = str(c.id)
                )]

            super().__init__(
                    placeholder="🌈 Select a color!",
                    options=options,
                    min_values=1,
            )

        async def callback(self, interaction: discord.Interaction):
            pattern = re.compile("\[C\].*")

            for r in interaction.user.roles:
                if pattern.match(r.name):
                    print(f"[colors] Removing color from {interaction.user}")
                    await interaction.user.remove_roles(r)

            for c in self.values:
                role = interaction.guild.get_role(int(c))
                print(f"[colors] Adding color to {interaction.user}")
                await interaction.user.add_roles(role)

            embed, view = self.cog.GetColorEmbed(self.ctx, self.colors, role)
            await interaction.response.edit_message(embed=embed, view=view)
