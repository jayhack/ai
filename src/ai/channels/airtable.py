import logging
from pyairtable import Api, Base, Table

logging.basicConfig(level=logging.INFO)

AIRTABLE_API_KEY = 'keygxE02sLmHSebja'
api = Api(AIRTABLE_API_KEY)

class AirtableInterface(object):
    id = 5
    name = 'AirtableInterface'

    def __init__(self, parent):
        self._post = parent._post
        self.agent_name = parent.name

    def send_message(self, payload):
        raise NotImplementedError