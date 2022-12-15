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

    def send_notifcation(self, processname, hostname, eventname, from_state):
        """
        Send a notification to a webhook
        """
        FORMATS = {
            "PROCESS_STATE_STARTING": [f"`{processname}` on `{hostname}` is **starting**...", 0x0C0FFAB],
            "PROCESS_STATE_RUNNING": [f"`{processname}` on `{hostname}` is now **running**!", 0x08FFF69],
            "PROCESS_STATE_BACKOFF": [f"`{processname}` on `{hostname}` failed. **Restarting**...", 0x0949494],
            "PROCESS_STATE_STOPPING": [f"`{processname}` on `{hostname}` is **stopping**...", 0x0F29D9D],
            "PROCESS_STATE_FATAL": [f"`{processname}` on `{hostname}`: **Failed to restart!**", 0x0FF0000],
            "PROCESS_STATE_EXITED": [f"`{processname}` on `{hostname}` **exited!**", 0x0FF0000],
            "PROCESS_STATE_STOPPED": [f"`{processname}` on `{hostname}` has **stopped!**", 0x0FF0000],
            "PROCESS_STATE_UNKNOWN": [f"`{processname}` on `{hostname}`: ***Unknown state! Uh oh!***", 0x0FF0000],
        }

        embed = Embed(description=FORMATS[eventname][0], color=FORMATS[eventname][1])
        webhook = SyncWebhook.from_url(self.webhook)

        webhook.send(embed=embed, username="Supervisor Status")

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

    def send_batch_notification(self):
        """
        Overrde ProcessStateMonitor function
        Determine whether to send any waiting notifications
        """
        for msg in self.batchmsgs:
            hostname, processname, from_state, eventname = msg.rsplit(";")
            processname = processname.split(":")[0]
            if processname in self.process_whitelist or "ALL" in self.process_whitelist:
                self.send_notifcation(processname, hostname, eventname, from_state)
            elif processname in self.process_blacklist or "ALL" in self.process_blacklist:
                return
            else:
                self.send_notifcation(processname, hostname, eventname, from_state)

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
