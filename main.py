from dotenv import load_dotenv
import discord, os

import roles, colors

load_dotenv()

TOKEN = os.getenv("DEBUG_TOKEN") if os.getenv("DEBUG") == True else os.getenv("PROD_TOKEN")
GUILDS = os.getenv("GUILDS").split(",")

bot = discord.Bot()

bot.add_cog(roles.Roles(bot, GUILDS))
bot.add_cog(colors.Colors(bot, GUILDS))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
