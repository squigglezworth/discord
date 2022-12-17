import discord
import os
import logging
from dotenv import load_dotenv

from cogs import imdb

# Setup logging formatter & stream handler
formatter = logging.Formatter(f"%(asctime)s - %(name)s - %(levelname)s - %(message)s")
formatter.default_msec_format = None
ch = logging.StreamHandler()
ch.setFormatter(formatter)
# Attach handlers to loggers and set logging level
logger = logging.getLogger("discord")
logger.addHandler(ch)
logger.setLevel(logging.WARNING)
logger = logging.getLogger("bot.imdb")
logger.addHandler(ch)
logger.setLevel(logging.INFO)

load_dotenv()

TOKEN = os.getenv("IMDB_TOKEN")

intents = discord.Intents.default()
intents.guilds = True
bot = discord.Bot(intents=intents)

bot.add_cog(imdb.Imdb(bot, db="sqlite:///imdb.sqlite"))


@bot.event
async def on_application_command(ctx):
    logger = logging.getLogger(f"bot.{ctx.command}")
    logger.info(f"Responding to '{ctx.user}' on '{ctx.guild.name}'")


@bot.event
async def on_ready():
    logger.info(f"Logged in as '{bot.user}' on {len(bot.guilds)} guilds")


@bot.event
async def on_guild_join(guild):
    logger.info(f"Joined guild '{guild.name}'")


bot.run(TOKEN)
