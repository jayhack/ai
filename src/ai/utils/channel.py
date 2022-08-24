from utils.api_interface import APIInterface
from utils.config import config


class Channel(APIInterface):
    id: int
    name: str
    subscription_id: int
    base_url: str

    def __init__(self, id: int, name: str, agent_name: str):
        self.id = id
        self.name = name
        self.base_url = f'{config["server_url"]}/agents/{agent_name}/channels/{id}'

    def __dict__(self):
        return {
            'id': self.id,
            'name': self.name
        }
