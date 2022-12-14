import logging
from typing import List, Union

import tweepy

from .channel import Channel
from ..app_id import AppID

logging.basicConfig(level=logging.INFO)


class TwitterChannel(Channel):
    app_id: AppID
    _api = None

    def authenticate(self):
        auth = tweepy.OAuthHandler(self.get_credential('API_KEY'), self.get_credential('API_SECRET_KEY'))
        auth.set_access_token(self.get_credential('ACCESS_TOKEN'), self.get_credential('ACCESS_TOKEN_SECRET'))
        return tweepy.API(auth)

    def update_status(self, text: str, image_urls: List[str] = None):
        return self.reply(None, text, image_urls)

    def reply(self, tweet_id: Union[int, None], text: str, image_urls: List[str] = None):
        if image_urls is None:
            image_urls = []
        json = {
            'agent_name': self.app_id.agent_name,
            'channel_name': self.name,
            'channel_id': self.id,
            'channel': {'id': self.id, 'name': self.name},
            'payload': {
                'tweet_id': tweet_id,
                'text': text,
                'image_urls': image_urls
            }
        }
        logging.info(f'[TwitterChannel] Sending message: {json}')
        response = self._post('/message', json)
        return response
