import logging
from slack import ChannelInterface
from github import Github

logging.basicConfig(level=logging.DEBUG)

jays_secret_key = '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' # only works for me
g = Github(jays_secret_key)

def get_repos():
    """Get all repos for a user"""
    return g.get_user().get_repos()

class GithubInterface(ChannelInterface):
    id = 4
    name = 'github'

    def __init__(self, parent):
        self._post = parent._post
        self.agent_name = parent.name

    def send_message(self, payload):
        json = {
            'agent_name': self.agent_name,
            'channel_name': self.name,
            'channel_id': self.id,
            'channel': {'id': self.id, 'name': self.name},
            'payload': payload
        }
        logging.info(f'[ GithubChannel ] Sending message: {json}')
        response = self._post('/message', json)
        if response is not None:
            logging.info(f'Successfully sent message: {dict(payload)}')
        else:
            logging.info(f'')
            print(f'Error: {response}')
        return response
