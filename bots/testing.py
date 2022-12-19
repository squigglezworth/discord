import bot
import discord
import logging
import os
from lib.webhook import WebhookHandler
from discord.ext import commands
from dotenv import load_dotenv

# from cogs import colors, memes, roles, publisher
import cogs

load_dotenv()
TOKEN = os.getenv("DEBUG_TOKEN")
GUILDS = [int(g) for g in os.getenv("GUILDS").split(",")] if os.getenv("GUILDS") else []

intents = discord.Intents.default()
intents.guilds = True
bot = bot.Bot("hideaway-debug", log_webhook="", intents=intents, debug_guilds=GUILDS)

# Setup webhook logging
log_webhook = os.getenv("LOG_WEBHOOK")
if log_webhook:
    webhook_handler = WebhookHandler(log_webhook)
    fmt = logging.Formatter(f"%(name)s - %(levelname)s - %(message)s")
    fmt.default_msec_format = None
    webhook_handler.setFormatter(fmt)
    bot.logger.addHandler(webhook_handler)


@commands.slash_command()
async def testing(ctx):
    """
    Testing!
    """
    bot.logger.info()
    await ctx.respond(content="test")


bot.run(TOKEN)
