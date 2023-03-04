# Build sqlite DB from JSON
# Check every X seconds if there's a new weekend
import logging
import discord
import os
import ast
import sqlite3
from discord.ext import tasks, commands
from datetime import datetime


class F1(commands.Cog):
    def __init__(self, bot, db, role, channel, perm_channel):
        bot.logger.info(f"Registering F1 notification task")

        self.logger = bot.logger
        self.bot = bot
        self.db = db
        self.role = role
        self.channel = channel
        self.perm_channel = perm_channel

        self.notification.start()

    @tasks.loop(hours=24)
    async def notification(self):
        self.logger.info("Looking for new F1 races")
        stmt = """
        SELECT events.ROWID, *
        FROM events
        LEFT JOIN tracks ON tracks.name = events.track
        WHERE NOT sent
        AND datetime(start) <= date('now', '+2 days', 'UTC')
        AND datetime(start) >= date('now', '-1 day', 'UTC')
        """

        con = sqlite3.connect(self.db)
        cur = con.cursor()
        results = cur.execute(stmt).fetchall()
        embeds = []
        for event in results:
            rowid = event[0]
            sessions = ast.literal_eval(event[7])
            track_record = (event[9], event[10], event[11], event[13])

            embed = discord.Embed(color=0xE6002B)
            embed.title = f"**{event[5]} {event[2]} — {event[6]}**\n"
            desc = ""
            for s in sessions:
                time = int(datetime.strptime(s[2], "%Y-%m-%dT%H:%M:%SZ").timestamp())
                desc += f"\n> **`{s[1]}`**<t:{time}:f> (<t:{time}:R>)"
            if track_record[0]:
                desc += f"\n\n***Track Record**: {track_record[1]} {track_record[0]} for {track_record[2]} in {track_record[3]}*"

            embed.description = desc
            embeds += [embed]
            cur.execute(f"UPDATE events SET sent = 1 WHERE ROWID = {rowid}")
            con.commit()

        channel = self.bot.get_channel(int(self.channel))
        await channel.send(content=f"<@&{self.role}>", embeds=embeds)

    @notification.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()
