from typing import Union
import logging
logging.basicConfig(level=logging.INFO)


class ChannelInterface(object):
    pass


class SlackChannel(ChannelInterface):
    id = 1
    name = 'slack'

    def __init__(self, parent):
        self._post = parent._post
        self.agent_name = parent.id.agent_name

    def send_message(self, content: Union[dict, str]):
        payload = content if type(content) is dict else {'text': content}
        json = {
            'agent_name': self.agent_name,
            'channel_name': self.name,
            'channel_id': self.id,
            'channel': {'id': self.id, 'name': self.name},
            'payload': {
                'text': content
            }
        }
        logging.info(f'[SlackChannel] Sending message: {json}')
        response = self._post('/message', json)
        if response is not None:
            logging.info(f'Successfully sent message: {dict(payload)}')
        else:
            logging.info(f'')
            print(f'Error: {response}')
        return response
