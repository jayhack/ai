from typing import NamedTuple
from typing import Union


class SlackBody(NamedTuple):
    text: str


MessageBody = Union[SlackBody]


class Message(object):
    """represents something happening (?)"""
    channel: str
    timestamp: str
    body: MessageBody

    def __init__(self, channel: str, timestamp: str, body: dict):
        self.channel = channel
        self.timestamp = timestamp
        self.body = SlackBody(text=body['text'])
