# A very simple implementation of a logging handler that posts to a (Discord) webhook
import logging
import requests
from logging.handlers import HTTPHandler


class WebhookHandler(logging.Handler):
    def __init__(self, webhook, color=0x0299AFF):
        logging.Handler.__init__(self)

        self.url = webhook
        self.color = color

    def mapLogRecord(self, record):
        record_modified = HTTPHandler.mapLogRecord(self, record)
        # record_modified schema: name, msg, args, levelname, levelno, pathname, filename, module, exc_info, exc_text, stack_info, lineno, funcName, created, msecs, relativeCreated, thread, threadName, processName, process, message, asctime
        # self.format returns the actual log message
        webhook_data = {"embeds": [{"color": self.color, "description": f"```{self.format(record)}```"}]}
        return webhook_data

    def emit(self, record):
        try:
            requests.post(self.url, json=self.mapLogRecord(record))
        except:
            self.handleError(record)
