from typing import Union

from .airtable import AirtableChannel
from .gh import GithubChannel
from .slack import SlackChannel
from .twitter import TwitterChannel
from ..app_id import AppID

ChannelUnionType = Union[AirtableChannel, SlackChannel, TwitterChannel, GithubChannel]


def create_channel(app_id: AppID, cdict: dict) -> ChannelUnionType:
    """Creates a channel specific to """
    channel_type = cdict['channel_type']
    if channel_type == 'Slack':
        return SlackChannel(app_id, cdict)
    elif channel_type == 'Twitter':
        return TwitterChannel(app_id, cdict)
    elif channel_type == 'GitHub':
        return GithubChannel(app_id, cdict)
    elif channel_type == 'Airtable':
        return AirtableChannel(app_id, cdict)
    else:
        raise ValueError(f'Unknown channel type: {channel_type}')
