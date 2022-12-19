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
        try:
            record_modified["data"] = {"embeds": [{"color": self.color, "description": f"```{self.format(record)}```"}]}
        except:
            pass
        return record_modified

    def emit(self, record):
        try:
            requests.post(self.url, json=self.mapLogRecord(record)["data"], timeout=10)
        except:
            self.handleError(record)
