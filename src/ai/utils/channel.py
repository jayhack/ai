from .api_interface import APIInterface
from .config import config
from ..app_id import AppID


class Channel(APIInterface):
    """
    API for interacting with channels like Slack, Notion, Github etc.

    Gets inherited by `channels.slack.SlackChannel` etc.

    import ai
    ai.slack.send_message(text='hello, world!')
    """
    id: int
    name: str
    app_id: AppID
    channel_type: str
    cdata: dict
    subscription_id: int
    base_url: str

    def __init__(self, channel_id: int, name: str, channel_type: str, cdata: dict, app_id: AppID):
        self.id = channel_id
        self.name = name
        self.channel_type = channel_type
        self.cdata = cdata
        base_url = f'{config["server_url"]}/channels/{id}'
        super(Channel, self).__init__(base_url, app_id)

    def __dict__(self):
        return {
            'id': self.id,
            'name': self.name
        }
