import logging
from typing import Union

import requests

from ..app_id import AppID

logging.basicConfig(level=logging.DEBUG)


class APIInterface(object):
    id: AppID
    base_url: str

    def __init__(self, id: AppID, base_url: str):
        self.id = id
        self.base_url = base_url

    @property
    def headers(self) -> dict:
        return {
            'user-name': self.id.user_name,
            'agent-name': self.id.agent_name,
            'agent-id': str(self.id.agent_id),
            'instance-id': str(self.id.instance_id),
        }

    def _get(self, endpoint: str) -> Union[dict, None]:
        print(self.headers)
        response = requests.get(f'{self.base_url}{endpoint}', headers=self.headers)
        return response.json()

    def _post(self, endpoint, data) -> dict:
        print(self.base_url)
        print(self.headers)
        response = requests.post(f'{self.base_url}{endpoint}', json=data, headers=self.headers)
        if response.status_code != 200:
            logging.info(f'_post Error: {response.content}')
            raise Exception(f'{response.content}')
        return response.json()
