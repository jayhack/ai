from typing import Any

from .api_interface import APIInterface
from .config import config
from .types import ModelQuery


class Model(APIInterface):
    id: int
    name: str
    agent_name: str
    base_url: str

    def __init__(self, id: int, name: str, agent_name: str):
        self.id = id
        self.name = name
        self.agent_name = agent_name
        self.base_url = f"{config['server_url']}/agents/{self.agent_name}/models/{self.id}"

    def query(self, raw_query: Any):
        query = ModelQuery(raw_query)
        response = self._post('/query', query.to_dict())
        return response['payload']['result']  # This is way too long
