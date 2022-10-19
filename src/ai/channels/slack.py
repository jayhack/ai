import logging
from typing import Union

from slack_sdk import WebClient

from .channel import Channel
from ..app_id import AppID

logging.basicConfig(level=logging.INFO)


class SlackChannel(Channel):
    app_id: AppID

    def authenticate(self):
        api = WebClient(self.get_credential('SLACK_ACCESS_TOKEN'))
        return api

    def send_message(self, content: Union[dict, str]):
        payload = content if type(content) is dict else {'text': content}
        json = {
            'agent_name': self.app_id.agent_name,
            'channel_name': self.name,
            'channel_id': self.id,
            'channel': {'id': self.id, 'name': self.name},
            'payload': payload
        }
        logging.info(f'[SlackChannel] Sending message: {json}')
        response = self._post('/message', json)
        return response
