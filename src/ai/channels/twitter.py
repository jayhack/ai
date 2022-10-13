import logging
from typing import List, Union

from .channel import Channel
from ..app_id import AppID
from .api_client_wrapper import APIClientWrapper
import tweepy

logging.basicConfig(level=logging.INFO)


def authenticate(api_key, api_key_secret, access_token, access_token_secret) -> tweepy.API:
    auth = tweepy.OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)


class TwitterChannel(Channel):
    app_id: AppID
    _api = None
    
    @property
    def api(self) -> APIClientWrapper:
        if not self._api:
            self._api = authenticate(self.get_credential('API_KEY'), self.get_credential('API_KEY_SECRET'),
                                     self.get_credential('ACCESS_TOKEN'), self.get_credential('ACCESS_TOKEN_SECRET'))
        return APIClientWrapper(self._api, self._post)

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
