import logging

from github import Github

from .api_client_wrapper import APIClientWrapper
from .channel import Channel
from ..app_id import AppID

logging.basicConfig(level=logging.INFO)


def get_repos():
    """Get all repos for a user"""
    return g.get_user().get_repos()


class GithubChannel(Channel):
    app_id: AppID
    _api: any = None

    def send_message(self, payload):
        json = {
            'agent_name': self.app_id.agent_name,
            'channel_name': self.name,
            'channel_id': self.id,
            'channel': {'id': self.id, 'name': self.name},
            'payload': payload
        }
        logging.info(f'[ GithubChannel ] Sending message: {json}')
        response = self._post('/message', json)
        if response is not None:
            logging.info(f'Successfully sent message: {dict(payload)}')
        else:
            logging.info(f'')
            print(f'Error: {response}')
        return response

    @property
    def api(self):
        key = self.get_credential('API_KEY')
        if not key:
            raise Exception('Github API key not found')
        if not self._api:
            self._api = Github(key)
        return APIClientWrapper(self._api, self._post)
