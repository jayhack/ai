import logging

from pyairtable import Api

from .channel import Channel
from ..app_id import AppID

logging.basicConfig(level=logging.INFO)

AIRTABLE_API_KEY = 'keygxE02sLmHSebja'
api = Api(AIRTABLE_API_KEY)


class AirtableChannel(Channel):
    app_id: AppID

    def send_message(self, payload):
        raise NotImplementedError

    @property
    def api(self):
        AIRTABLE_API_KEY = self.get_credential('API_KEY')
        return Api(AIRTABLE_API_KEY)
