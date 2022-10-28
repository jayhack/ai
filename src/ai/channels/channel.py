from typing import Union

from .api_client_wrapper import APIClientWrapper
from ..app_id import AppID
from ..utils.api_interface import APIInterface
from ..utils.config import config

ChannelType = Union['Slack', 'Twitter', 'GitHub', 'Airtable']


class Channel(APIInterface):
    id: int
    name: str
    app_id: AppID
    channel_type: ChannelType
    cdata: dict
    subscription_id: int
    base_url: str
    _api: any = None

    def __init__(self, app_id: AppID, cdata: dict):
        self.id = cdata['id']
        self.name = cdata['name']
        self.channel_type = cdata['channel_type']
        self.cdata = cdata
        base_url = f'{config["server_url"]}/agents/channel'
        super(Channel, self).__init__(app_id, base_url)

    def authenticate(self):
        """returns an API object"""
        raise NotImplementedError

    @property
    def api(self):
        if not self._api:
            self._api = self.authenticate()
        return APIClientWrapper(self._api, self._post)

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
