from typing import Any

from .api_interface import APIInterface
from .config import config
from .custom_types import ModelQuery


class Model(APIInterface):
    id: int
    name: str
    id: int
    base_url: str

    def __init__(self, id: int, name: str, agent_id: int):
        self.id = id
        self.name = name
        self.agent_id = agent_id
        self.base_url = f"{config['server_url']}/agents/models"

    def query(self, raw_query: Any, use_active_prompt=False, prompt_id=None) -> dict:
        query = ModelQuery(raw_query)
        d = query.to_dict()
        d['model_id'] = self.id
        d['agent_id'] = self.agent_id
        d['use_active_prompt'] = use_active_prompt
        if prompt_id:
            d['prompt_id'] = prompt_id
        response = self._post('/query', d)
        return response['payload']['result']  # This is way too long
