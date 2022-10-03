import logging
from dataclasses import dataclass
from typing import Union
from ..app_id import AppID

import requests

logging.basicConfig(level=logging.DEBUG)


class APIInterface(object):
    id: AppID
    base_url: str
    headers: Union[dict, None] = None

    def __init__(self, base_url: str, app_id: AppID):
        self.base_url = base_url
        self.id = app_id
        self.headers = {
            'user_name': self.id.user_name,
            'agent_name': self.id.agent_name,
            'agent_id': self.id.agent_instance_id,
            'agent_instance_id': self.id.agent_instance_id,
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
