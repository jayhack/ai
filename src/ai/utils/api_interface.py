import logging
from typing import Union

import requests


class APIInterface(object):
    base_url: str

    def _get(self, endpoint) -> Union[dict, None]:
        response = requests.get(f'{self.base_url}{endpoint}')
        if response.status_code != 200:
            return None
        return response.json()

    def _post(self, endpoint, data) -> Union[dict, None]:
        response = requests.post(f'{self.base_url}{endpoint}', json=data)
        if response.status_code != 200:
            logging.info(f'_post Error: {response.content}')
            return None
        return response.json()
