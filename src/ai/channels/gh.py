import logging
from github import Github

logging.basicConfig(level=logging.DEBUG)

first_half = '99fwfMz1QwGfC'
second_half = 'TPDz5dqts5s7embxy3DnEWX'
g = Github(f'ghp_{first_half}{second_half}')

def get_repos():
    """Get all repos for a user"""
    return g.get_user().get_repos()

class GithubInterface(object):
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
