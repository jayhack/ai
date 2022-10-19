import logging

from pyairtable import Api

from .channel import Channel
from ..app_id import AppID

logging.basicConfig(level=logging.INFO)


class AirtableChannel(Channel):
    app_id: AppID

    def authenticate(self):
        return Api(self.get_credential('API_KEY'))
