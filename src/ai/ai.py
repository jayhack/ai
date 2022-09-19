import logging
import asyncio
from typing import Dict
from typing import List

import uvicorn
from fastapi import APIRouter
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import RedirectResponse

from .utils.api_interface import APIInterface
from .utils.channel import Channel
from .channels.gh import g, GithubInterface
from .channels.slack import ChannelInterface, SlackChannel
from .channels.airtable import AirtableInterface, api as airtable_api
from .utils.config import config
from .utils.message import Message
from .utils.model import Model

logging.basicConfig(level=logging.DEBUG)

all_channels = [SlackChannel]


class ChannelInput(BaseModel):
    id: int
    name: str


class TriggerInput(BaseModel):
    id: int
    timestamp: str
    channel: ChannelInput
    producer_id: int
    body: Dict


def extract_message(t: TriggerInput) -> Message:
    return Message(
        channel=t.channel.name,
        timestamp=t.timestamp,
        body=dict(t.body)
    )


app = FastAPI()
router = APIRouter()

default_channels = ['slack', 'github', 'airtable']
default_models = ['openai/gpt-3', 'stability-ai/stable-diffusion']

class AI(APIInterface):
    """Main interface"""
    id: int
    name: str
    base_url = config['server_url']
    app = None
    handler = None
    channels: List[Channel]
    channel_interfaces: Dict[str, ChannelInterface]
    models: List[Model]

    def init(self, name: str, url: str, channels: List[str] = default_channels, models: List[str] = default_models):
        self.name = name
        self.init_data = {
            'name': name,
            'url': url,
            'channels': channels,
            'models': models
        }
        self.base_url = f'{config["server_url"]}/agents'
        self._register()

    def _register(self):
        data = self._post(f'/register', {
            'name': self.name,
            'url': self.init_data['url'],
            'channels': self.init_data['channels'],
            'models': self.init_data['models']
        })
        if not data:
            raise Exception('Could not establish connection to server')
        else:
            if data['is_new']:
                logging.info(f'Registered new agent: {self.name}')
            else:
                logging.info(f'Registered returning agent: {self.name}')
        self.id = data['agent']['id']
        self.models = [Model(m['id'], m['name'], self.name) for m in data['models']]
        self.channels = [Channel(c['id'], c['name'], self.name) for c in data['channels']]
        self.channel_interfaces = {c.name: c(self) for c in all_channels if self.has_channel(c.name)}
        print('#####################################################')
        print('# ', config['admin_url'].format(agent_name=self.name))
        print('#####################################################')

    @property
    def slack(self):
        return self.channel_interfaces['slack']

    @property
    def github(self):
        return self.channel_interfaces['github']

    @property
    def github_api(self):
        return g

    @property
    def airtable_api(self):
        return airtable_api

    ####################################################################################################################
    # MODELS
    ####################################################################################################################

    def get_model(self, model_name) -> Model:
        if model_name not in [m.name for m in self.models]:
            raise Exception(f'No such model: {model_name}')
        return [m for m in self.models if m.name == model_name][0]

    def get_models(self) -> List[Model]:
        return self.models

    def load_models(self) -> List[Model]:
        payload = self._get('/models')
        self.models = [Model(m['id'], m['name'], self.name) for m in payload['models']]
        return self.models

    ####################################################################################################################
    # CHANNELS
    ####################################################################################################################

    def get_channel(self, name: str) -> Channel:
        if name not in [c.name for c in self.channels]:
            raise Exception(f'No such channel: {name}')
        return [c for c in self.channels if c.name == name][0]

    def get_channels(self) -> List[Channel]:
        return self.channels

    def has_channel(self, name: str) -> bool:
        return len([c for c in self.channels if c.name == name]) > 0

    def load_channels(self) -> List[Channel]:
        payload = self._get('/channels')
        self.channels = [Channel(c['id'], c['name'], self.name) for c in payload['channels']]
        self.channel_interfaces = {c.name: c for c in all_channels if self.has_channel(c.name)}
        return self.channels

    ####################################################################################################################
    # RUNNING
    ####################################################################################################################

    async def handle_healthcheck(self):
        return {'healthcheck': 'hello world!'}

    async def redirect_dashboard(self):
        base_url = 'https://devai.retool.com/embedded/public/1c65ff6f-4485-489a-b151-205e635b7f7b'
        return RedirectResponse(
            url=f'{base_url}#agent_name={self.name}'
        )

    async def handle_trigger(self, input: TriggerInput):
        message = extract_message(input)
        asyncio.create_task(self.handler(message))
        return {'status': 'success'}

    def start(self, handler, port=8080):
        self.app = app
        self.handler = handler
        router.add_api_route('/', endpoint=self.redirect_dashboard, methods=['GET'])
        router.add_api_route('/healthcheck', endpoint=self.handle_healthcheck, methods=['GET'])
        router.add_api_route('/io', endpoint=self.handle_trigger, methods=['POST'])
        self.app.include_router(router)
        uvicorn.run(self.app, host="0.0.0.0", port=port)


ai = AI()
