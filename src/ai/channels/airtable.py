import logging

from pyairtable import Api

from .channel import Channel
from ..app_id import AppID

logging.basicConfig(level=logging.INFO)


class AirtableChannel(Channel):
    app_id: AppID

    def send_message(self, payload):
        raise NotImplementedError

    @property
    def api(self):
        key = self.get_credential('API_KEY')
        if not key:
            raise Exception('Airtable API key not found')
        return Api(key)
