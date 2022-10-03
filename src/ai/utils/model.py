from typing import Any

from .api_interface import APIInterface
from .config import config
from .custom_types import ModelQuery
from ..app_id import AppID


class Model(APIInterface):
    id: int
    name: str
    app_id: AppID

    def __init__(self, id: int, name: str, app_id: AppID):
        self.id = id
        self.name = name
        self.app_id = app_id
        base_url = f"{config['server_url']}/agents/models"
        super(Model, self).__init__(base_url, app_id)

    def query(self, raw_query: Any, use_active_prompt=False, prompt_id=None) -> dict:
        """TODO: Clean this up, better define ModelQuery relations etc."""
        data = ModelQuery(raw_query).to_dict()
        data['model_name'] = self.name
        data['use_active_prompt'] = use_active_prompt
        if prompt_id:
            data['prompt_id'] = prompt_id
        response = self._post('/query', data)
        return response['payload']['result']  # This is way too long
