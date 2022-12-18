from .. import bot
import discord
import os
from dotenv import load_dotenv
from cogs import imdb

load_dotenv()
TOKEN = os.getenv("IMDB_TOKEN")

intents = discord.Intents.default()
intents.guilds = True
bot = bot.Bot("imdb", intents=intents)

bot.add_cog(imdb.Imdb(bot, db="sqlite:///imdb.sqlite"))


bot.run(TOKEN)
