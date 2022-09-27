import logging
from typing import List

logging.basicConfig(level=logging.INFO)


class ChannelInterface(object):
    pass


class TwitterChannel(ChannelInterface):
    id = 2
    name = 'twitter'

    def __init__(self, parent):
        self._post = parent._post
        self.agent_name = parent.name

    def reply(self, tweet_id: int, text: str, images: List[str]):
        json = {
            'agent_name': self.agent_name,
            'channel_name': self.name,
            'channel_id': self.id,
            'channel': {'id': self.id, 'name': self.name},
            'payload': {
                'tweet_id': tweet_id,
                'text': text,
                'images': images
            }
        }
        logging.info(f'[TwitterChannel] Sending message: {json}')
        response = self._post('/message', json)
        if response is not None:
            logging.info(f'Successfully sent message: {dict(json["payload"])}')
        else:
            logging.info(f'Error: {response}')
        return response
