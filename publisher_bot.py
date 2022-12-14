import discord, os, logging
from dotenv import load_dotenv

from cogs import publisher

# Setup logging formatter & stream handler
formatter = logging.Formatter(f"%(asctime)s - %(name)s - %(levelname)s - %(message)s")
formatter.default_msec_format = None
ch = logging.StreamHandler()
ch.setFormatter(formatter)
# Attach handlers to loggers and set logging level
logger = logging.getLogger("discord")
logger.addHandler(ch)
logger.setLevel(logging.WARNING)
logger = logging.getLogger("publisher-bot")
logger.addHandler(ch)
logger.setLevel(logging.INFO)

load_dotenv()

PUBLISHER_TOKEN = os.getenv("PUBLISHER_TOKEN")

bot = discord.Bot()

bot.add_cog(publisher.AutoPublisher(bot))


@bot.event
async def on_application_command(ctx):
    logger = logging.getLogger(f"bot.{ctx.command}")
    logger.info(f"Responding to {ctx.user}")


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} on {len(bot.guilds)} guilds")


bot.run(PUBLISHER_TOKEN)
