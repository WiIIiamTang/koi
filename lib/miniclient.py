import logging
import requests
import time


class MiniClient:
    def __init__(self, logger, token, default_channel_id=None):
        self.logger = logger or logging.getLogger(__name__)
        self.token = token
        self.send_message_base = "https://discord.com/api/v9/channels/{}/messages"
        self.read_messages_base = (
            "https://discord.com/api/v9/channels/{}/messages?limit={}"
        )
        self.default_channel_id = default_channel_id
        if self.token is None:
            raise ValueError("Token is None")

    def handle_exceptions(self, func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.logger.exception(e)

        return wrapper

    def timebreak(self, func, seconds=1):
        def wrapper(*args, **kwargs):
            if not self.first_time:
                time.sleep(seconds)
                self.first_time = False
            return func(*args, **kwargs)

        return wrapper

    @handle_exceptions()
    @timebreak()
    def send_message(self, channel_id, message):
        ch_id = channel_id or self.default_channel_id
        self.logger.info(f"Sending message to {ch_id} with content {message}")
        r = requests.post(
            self.send_message_base.format(ch_id),
            data={"content": message},
            headers={"Authorization": self.token},
        )
        self.logger.info(f"Response: {r.status_code} {r.content}")

    @handle_exceptions()
    @timebreak()
    def read_messages(self, channel_id, limit=2):
        ch_id = channel_id or self.default_channel_id
        self.logger.info(f"Reading {limit} messages from {ch_id}")
        r = requests.get(
            self.read_messages_base.format(ch_id, limit),
            headers={"Authorization": self.token},
        )
        self.logger.info(f"Response: {r.status_code} {r.content}")

        return r.json()
