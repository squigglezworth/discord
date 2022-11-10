from dotenv import load_dotenv
import discord, os

from cogs import roles, colors

load_dotenv()

TOKEN = os.getenv("DEBUG_TOKEN") if os.getenv("DEBUG") == "True" else os.getenv("PROD_TOKEN")
GUILDS = [int(g) for g in os.getenv("GUILDS").split(",")]

bot = discord.Bot(debug_guilds=GUILDS)

# There can be a max of 5 menus
menus = [
    {
        "placeholder": "EVE Online roles",
        "roles": [
            # [<id>, "<description>", "<emoji>"]
            [880572127823159366, "", ""],
            [880572192872611871, "", ""],
            [885936958394748950, "", ""]
        ]
    },
    {
        "placeholder": "🏳️‍🌈 LGBT roles - Grant access to the #🌈lgbt channel",
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
        "roles": [
            # [<id>, "<description>", "<emoji>"]
            [1037691564954238996, "Grants access to the neurodivergent chat channel", ""],
            [972970423744610374, "", ""],
            [972970633174614058, "", ""],
            [972970544670584852, "", ""]
        ]
    }
]
# List of role IDs to exclude from the listing of the user's current roles
# @everyone is automatically excluded
exclude = [983269188036608050,637192413584293889]

bot.add_cog(roles.Roles(bot, exclude, menus, GUILDS))

# Prefix your color roles with [C] (or change the prefix)
bot.add_cog(colors.Colors(bot, "[C]", GUILDS))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
