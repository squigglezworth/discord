import bot
import discord
import logging
import os
from utils.webhook import WebhookHandler
from dotenv import load_dotenv
from cogs import simple_publisher

load_dotenv()
TOKEN = os.getenv("PUBLISHER_TOKEN")

intents = discord.Intents.default()
intents.guilds = True
bot = bot.Bot("publisher", intents=intents)

db = os.getenv("PUBLISHER_DB")
if not db:
    logging.getLogger("discord.bot").error("Please specify a PUBLISHER_DB in the .env file")
    # There's probably a better way of exiting... oh well
    exit()
bot.add_cog(simple_publisher.Publisher(bot))

# Setup webhook logging
log_webhook = os.getenv("PUBLISHER_LOG_WEBHOOK")
if log_webhook:
    handler = WebhookHandler(log_webhook, color=0x0FF5338)
    fmt = logging.Formatter(f"%(name)s - %(levelname)s - %(message)s")
    fmt.default_msec_format = None
    handler.setFormatter(fmt)
    handler.setLevel(logging.INFO)

    logging.getLogger("discord").addHandler(handler)
    bot.logger.addHandler(handler)


bot.run(TOKEN)
