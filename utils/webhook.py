# A very simple implementation of a logging handler that posts to a (Discord) webhook
import logging
from logging.handlers import HTTPHandler


class WebhookHandler(logging.Handler):
    def __init__(self, webhook):
        import requests

        logging.Handler.__init__(self)

        self.url = webhook
        self.session = requests.Session()

    def mapLogRecord(self, record):
        record_modified = HTTPHandler.mapLogRecord(self, record)
        try:
            record_modified["content"] = f"`{self.format(record)}`"
        except:
            pass
        return record_modified

    def emit(self, record):
        try:
            self.session.post(self.url, json=self.mapLogRecord(record), timeout=10)
        except:
            self.handleError(record)
