import bot
import discord
import os
from utils.webhook import WebhookHandler
from dotenv import load_dotenv
from cogs import publisher

load_dotenv()
TOKEN = os.getenv("PUBLISHER_TOKEN")

intents = discord.Intents.default()
intents.guilds = True
bot = bot.Bot("publisher", intents=intents)

bot.add_cog(publisher.AutoPublisher(bot, db="/home/squigz/dev/bots/publisher.sqlite"))

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
