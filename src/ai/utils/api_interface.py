import logging
from typing import Union

import requests

logging.basicConfig(level=logging.DEBUG)


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
            raise Exception(f'{response.content}')
        return response.json()
