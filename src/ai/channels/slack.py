from typing import Union


class ChannelInterface(object):
    pass


class SlackChannel(ChannelInterface):
    id = 1
    name = 'slack'

    def __init__(self, parent):
        self._post = parent._post
        self.agent_name = parent.name

    def send_message(self, content: Union[dict, str]):
        payload = content if type(content) is dict else {'text': content}
        response = self._post('/message', {
            'agent_name': self.agent_name,
            'channel_name': self.name,
            'channel_id': self.id,
            'channel': {'id': self.id, 'name': self.name},
            'payload': {
                'text': content
            }
        })
        if response is not None:
            print(f'Successfully sent message: {dict(payload)}')
        else:
            print(f'Error: {response}')
        return response
