from typing import Union

from ..app_id import AppID
from ..utils.api_interface import APIInterface
from ..utils.config import config

ChannelType = Union['Slack', 'Twitter', 'GitHub', 'Airtable']


class Channel(APIInterface):
    """
    API for interacting with channels like Slack, Notion, Github etc.

    Gets inherited by `channels.slack.SlackChannel` etc.

    import ai
    ai.slack.send_message(text='hello, world!')
    """
    id: int
    name: str
    app_id: AppID
    channel_type: ChannelType
    cdata: dict
    subscription_id: int
    base_url: str

    def __init__(self, app_id: AppID, cdata: dict):
        self.id = cdata['id']
        self.name = cdata['name']
        self.channel_type = cdata['channel_type']
        self.cdata = cdata
        base_url = f'{config["server_url"]}/agents/channel'
        super(Channel, self).__init__(base_url, app_id)

    def get_credential(self, cred_name: str):
        all_creds = {x['key']: x['value'] for x in self.cdata['credentials']}
        return all_creds.get(cred_name, None)

    def __dict__(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def __str__(self):
        return f'<Channel: name={self.name} type={self.channel_type} id={self.id}>'
