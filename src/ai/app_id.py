from dataclasses import dataclass
from typing import Union


@dataclass
class AppID:
    """Describes current app"""
    user_name: str
    agent_name: str
    agent_id: Union[int, None]
    instance_id: Union[int, None]
