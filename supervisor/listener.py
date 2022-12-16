# Forked from https://github.com/slara/superslacker
# Trimmed-down and adapted for Discord webhooks

from superlance.process_state_monitor import ProcessStateMonitor
from supervisor import childutils
from discord import SyncWebhook, Embed
import argparse, socket


class listener(ProcessStateMonitor):
    EVENTS = [
        # Full name, short name, image
        ["PROCESS_STATE_STARTING", "STARTING"],
        ["PROCESS_STATE_RUNNING", "RUNNING"],
        ["PROCESS_STATE_BACKOFF", "BACKOFF"],
        ["PROCESS_STATE_STOPPING", "STOPPING"],
        ["PROCESS_STATE_FATAL", "FATAL"],
        ["PROCESS_STATE_EXITED", "EXITED"],
        ["PROCESS_STATE_STOPPED", "STOPPED"],
        ["PROCESS_STATE_UNKNOWN", "UNKNOWN"],
    ]
    EMBEDS = {
        # Provide a dict in the form of a Discord Embed Object - https://discord.com/developers/docs/resources/channel#embed-object
        "PROCESS_STATE_STARTING": {
            "description": "`{processname}` on `{hostname}` is **starting**...",
            "color": 0x0C0FFAB,
        },
        "PROCESS_STATE_RUNNING": {
            "description": "`{processname}` on `{hostname}` is now **running**!",
            "author": {"name": "Running!", "url": "", "icon_url": "https://cdn.discordapp.com/attachments/666629290024108085/1053169984685211678/check.png"},
            "color": 0x08FFF69,
        },
        "PROCESS_STATE_BACKOFF": {
            "description": "`{processname}` on `{hostname}` failed. **Restarting**...",
            "color": 0x0949494,
        },
        "PROCESS_STATE_STOPPING": {
            "description": "`{processname}` on `{hostname}` is **stopping**...",
            "color": 0x0F29D9D,
        },
        "PROCESS_STATE_FATAL": {
            "description": "`{processname}` on `{hostname}` **failed to restart!**",
            "color": 0x0FF0000,
        },
        "PROCESS_STATE_EXITED": {
            "description": "`{processname}` on `{hostname}` **exited!**",
            "color": 0x0FF0000,
        },
        "PROCESS_STATE_STOPPED": {
            "description": "`{processname}` on `{hostname}` has **stopped!**",
            "author": {"name": "Stopped!", "url": "", "icon_url": "https://cdn.discordapp.com/attachments/666629290024108085/1053171912873873438/circle865.png"},
            "color": 0x0FF0000,
        },
        "PROCESS_STATE_UNKNOWN": {
            "description": "`{processname}` on `{hostname}`: ***Unknown state! Uh oh!***",
            "color": 0x0FF0000,
        },
    }

    def __init__(self, **args):
        self.webhook = args.get("webhook")
        self.process_blacklist = []
        self.process_whitelist = []

        if args.get("blacklist"):
            self.process_blacklist = ["{}".format(e.strip()) for e in args.get("blacklist", None).split(",")]

        if args.get("whitelist"):
            self.process_whitelist = ["{}".format(e.strip()) for e in args.get("whitelist", None).split(",")]

        # Initialize the ProcessStateMonitor and set some vars for it
        ProcessStateMonitor.__init__(self, **args)

        self.eventname = args.get("eventname")
        self.interval = args.get("interval") / 60
        self.hostname = socket.gethostname()

        # Subscribe to all events, and then override if any events were specified
        self.process_state_events = [e[0] for e in self.EVENTS]
        if args.get("events"):
            self.process_state_events = ["PROCESS_STATE_{}".format(e.strip().upper()) for e in args.get("events") if e in [e[1] for e in self.EVENTS]]

    def chunk(self, notifications, n=10):
        for i in range(0, len(notifications), n):
            yield notifications[i : i + n]

    def send_notifications(self, notifications):
        """
        Send a notification to a webhook
        Chunks up to 10 embeds per message
        """

        webhook = SyncWebhook.from_url(self.webhook)

        for n in list(self.chunk(notifications)):
            embeds = []
            for e in n:
                info = {"processname": e[0], "hostname": e[1], "eventname": e[2], "from_state": e[3]}
                embed = Embed.from_dict(self.EMBEDS[e[2]])
                embed.description.format(**info)
                embeds += [embed]

            webhook.send(embeds=embeds, username="Supervisor Status")

    def send_batch_notification(self):
        """
        Overrde ProcessStateMonitor function
        Determine whether to send any waiting notifications
        """
        notifications = []
        for msg in self.batchmsgs:
            hostname, processname, from_state, eventname = msg.rsplit(";")
            processname = processname.split(":")[0]
            if processname in self.process_whitelist or "ALL" in self.process_whitelist:
                notifications.append([processname, hostname, eventname, from_state])
            elif processname in self.process_blacklist or "ALL" in self.process_blacklist:
                return
            else:
                notifications.append([processname, hostname, eventname, from_state])
        self.send_notifications(notifications)

    def get_process_state_change_msg(self, headers, payload):
        pheaders, pdata = childutils.eventdata(payload + "\n")
        return "{hostname};{groupname}:{processname};{from_state};{event}".format(hostname=self.hostname, event=headers["eventname"], **pheaders)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--webhook", required=True, help="Webhook URL")
    parser.add_argument("--events", nargs="+", choices=[e[1] for e in listener.EVENTS], help="One or more Supervisor event(s) to send notifications for. If unspecified, all events will be used")
    parser.add_argument("--blacklist", help="Comma-separated list of applications for which not to send notifications")
    parser.add_argument("--whitelist", help="Comma-separated list of applications always to monitor")
    parser.add_argument("--eventname", choices=["TICK_5", "TICK_60", "TICK_3600"], default="TICK_5", help="How often to prepare notifications. 5, 60, or 3600 seconds")
    parser.add_argument("--interval", default=5, help="How often to send any prepared notifications. Default is 5 seconds")

    options = parser.parse_args()

    listener = listener(**options.__dict__)
    # Start the ProcessStateMonitor main loop
    listener.run()
