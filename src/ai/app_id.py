from dataclasses import dataclass
from typing import Union


@dataclass
class AppID:
    """Describes current app"""
    user_name: str
    agent_name: str
    agent_id: Union[int, None]
    instance_id: Union[int, None]
    creds: Union[dict, None]

    def get_creds(self, channel: str, key: str) -> str:
        return self.creds.get(channel, None)
