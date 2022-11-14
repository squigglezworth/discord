from dotenv import load_dotenv
import discord, os

import RoleMenus
from cogs import colors

load_dotenv()

TOKEN = os.getenv("DEBUG_TOKEN") if os.getenv("DEBUG") == "True" else os.getenv("PROD_TOKEN")
GUILDS = [int(g) for g in os.getenv("GUILDS").split(",")] if os.getenv("GUILDS") else []

# settings = {
# }

settings = {
    "roles": {
        "name": "roles",
        "description": "Add/remove various roles from yourself. Tag them to share links, chat with others, etc",
        # Embed content
        "embed": "*Hello <@{ctx.user.id}>, your current roles are:\n{RolesList}\n\nUse the menus below to add or remove roles.*",
        # No limit
        "max_one": 0,
        # List of role IDs to exclude from the listing of the user's current roles
        # @everyone is automatically excluded
        "exclude": [983269188036608050,637192413584293889],
        "dropdowns": [
            {
                "placeholder": "EVE Online roles",
                "randomize": 0,
                "roles": [
                    # [<id>, "<description>", "<emoji>"]
                    [880572127823159366, "", ""],
                    [880572192872611871, "", ""],
                    [885936958394748950, "", ""]
                ]
            },
            {
                "placeholder": "🏳️‍🌈 LGBT roles - Grant access to the #🌈lgbt channel",
                "randomize": 0,
                "roles": [
                    # [<id>, "<description>", "<emoji>"]
                    [1007573574082642011, "", ""],
                    [1007573880728199188, "", ""],
                    [1007573890198949920, "", ""],
                    [1007573993135558679, "", ""],
                    [1007575326227972209, "", ""],
                    [1007623293811032157, "", ""],
                    [1007623250118987796, "", ""],
                    [1007573999699628072, "", ""],
                    [1007574163302658081, "", ""],
                    [1007574166242861117, "", ""]
                ]
            },
            {
                "placeholder": "Misc/Topic roles",
                "randomize": 0,
                "roles": [
                    # [<id>, "<description>", "<emoji>"]
                    [1037691564954238996, "Grants access to the neurodivergent chat channel", ""],
                    [972970423744610374, "", ""],
                    [972970633174614058, "", ""],
                    [972970544670584852, "", ""]
                ]
            }
        ]
    },
    "icons": {
        # /role <name>
        "name": "icons",
        # Command description
        "description": "Stand out with a fancy icon that will appear next to your name in chat",
        # Embed content
        "embed": "*Hello <@{ctx.user.id}>, your current icon role is {ShortRolesList}\n\nSelect one below, and it'll show up next to your name in chat!*",
        # Allow only 1 of *all* the provided roles
        "max_one": 1,
        # List of role IDs to exclude from the listing of the user's current roles
        # @everyone is automatically excluded
        "exclude": [],
        "dropdowns": [
            {
                "placeholder": "🦉 Animal Icons",
                "randomize": 1,
                "roles": [
                    [1041543542423691336,"","🦑"],
                    [1041543751845290024,"","🐳"],
                    [1041543812272623737,"","🦀"],
                    [1041719288437944410,"", "🦉"]
                ]
            },
            {
                "placeholder": "🏳️‍🌈 LGBT Icons",
                "randomize": 1,
                "roles":  [
                    [1041321819984105512,"","<:LesbianPride:1007578778035290112>"],
                    [1041321894927937646,"","<:GayPride:1007578774897954867>"],
                    [1041321919984713848,"","<:BisexualPride:1007578776630198303>"],
                    [1041321940998168627,"","🏳️‍⚧️"],
                    [1041321961697071214,"","♂️"],
                    [1041322000469196850,"","♀️"],
                    [1041322026234822716,"","⚧"],
                    [1041322212982018059,"","<:AsexualPride:1007623033189568562>"],
                    [1041322264815218688,"","<:AromanticPride:1007623034959581245>"],
                    [1041322146636513360,"","<:NeurodiversityPride:1037203581733974026>"]
                ]
            },
            {
                "placeholder": "🥐 Misc. Icons",
                "randomize": 1,
                "roles": [
                    [1041322728365506620,"","<:logo:875904386444967946>"],
                    [1041322473783840888,"","<:corplogo:787272419127722004>"],
                    [1041322094543261716,"","<:freighter:1040091624715341865>"],
                    [1041322195701481502,"","📚"],
                    [1041335138434424942,"","🥐"]
                ]
            }
        ]
    }
}

bot = discord.Bot(debug_guilds=GUILDS)

RoleMenus.register(bot, settings)

# Prefix your color roles with [C] (or change the prefix)
bot.add_cog(colors.Colors(bot, "[C]", GUILDS))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
