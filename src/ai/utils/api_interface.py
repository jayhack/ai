import logging
from typing import Union

import requests

from ..app_id import AppID

logging.basicConfig(level=logging.DEBUG)


class APIInterface(object):
    id: AppID
    base_url: str

    def __init__(self, base_url: str, app_id: AppID):
        self.base_url = base_url
        self.id = app_id

    @property
    def headers(self) -> dict:
        return {
            'user-name': self.id.user_name,
            'agent-name': self.id.agent_name,
            'agent-id': str(self.id.agent_id),
            'instance-id': str(self.id.instance_id),
        }

    def _get(self, endpoint: str) -> Union[dict, None]:
        response = requests.get(f'{self.base_url}{endpoint}', headers=self.headers)
        return response.json()

    def _post(self, endpoint, data) -> Union[dict, None]:
        response = requests.post(f'{self.base_url}{endpoint}', json=data, headers=self.headers)
        if response.status_code != 200:
            logging.info(f'_post Error: {response.content}')
            raise Exception(f'{response.content}')
        return response.json()
