from typing import NamedTuple
from typing import Union
from typing import Dict


class SlackBody(NamedTuple):
    text: str


MessageBody = Union[SlackBody]


class Message(object):
    """represents something happening (?)"""
    channel: str
    timestamp: str
    body: Dict

    def __init__(self, channel: str, timestamp: str, body: dict):
        self.channel = channel
        self.timestamp = timestamp
        self.body = body
