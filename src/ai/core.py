import asyncio
import logging
import os
from typing import Callable
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

import uvicorn
from fastapi import APIRouter
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import RedirectResponse

from .app_id import AppID
from .channels.airtable import api as airtable_api
from .channels.gh import g
# from .channels.notion import notion_api
from .channels.slack import ChannelInterface, SlackChannel
from .channels.twitter import TwitterChannel
from .utils.api_interface import APIInterface
from .utils.channel import Channel
from .utils.config import config
from .utils.message import Message
from .utils.model import Model

logging.basicConfig(level=logging.INFO)

all_channels = [SlackChannel, TwitterChannel]


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

default_channels: List[Channel] = ['slack', 'twitter']
default_models: List[Model] = ['openai/gpt-3', 'stability-ai/stable-diffusion']


class AI(APIInterface):
    """Main interface"""
    id: AppID
    app_url: str
    base_url = config['server_url']
    app = None
    handler = None
    channels: List[Channel]
    channel_interfaces: Dict[str, ChannelInterface]
    models: List[Model]

    ####################################################################################################################
    # INITIALIZATION
    ####################################################################################################################

    @classmethod
    def is_local_dev(cls):
        """Used for development; returns True if this is not on Replit"""
        return 'REPL_OWNER' not in os.environ

    @classmethod
    def get_app_metadata(cls) -> Tuple[str, str, str]:
        """Assumes Replit"""
        if cls.is_local_dev():
            return 'demo-agent', 'demo-user', 'http://localhost:8081'
        app_name = os.environ['PYTHONPATH'].split('/')[3]
        user_name = os.environ['REPL_OWNER']
        app_url = f'https://{app_name}.{user_name}.repl.co'
        return app_name, user_name, app_url

    def __init__(self):
        app_name, user_name, self.app_url = self.get_app_metadata()
        self.base_url = config['server_url'] + '/agents'
        self.id = AppID(
            user_name=user_name,
            agent_name=app_name,
            agent_id=None,
            instance_id=None
        )
        super(AI, self).__init__(self.base_url, self.id)

    def register(self, channels: List[str], models: List[str]):
        """Announces presence of this agent to the server"""
        self.channels = channels or default_channels
        self.models = models or default_models
        data = self._post(f'/register', {
            'app_name': self.id.agent_name,
            'user_name': self.id.user_name,
            'url': self.app_url,
            'channels': self.channels,
            'models': self.models
        })
        if not data:
            raise Exception('Could not establish connection to server')
        else:
            if data['is_new']:
                logging.info(f'Registered new agent: {self.id.agent_name}')
            else:
                logging.info(f'Registered returning agent: {self.id.agent_name}')
        self.id.agent_id = data['agent']['id']
        self.id.instance_id = data['instance']['id']
        self.models = [Model(m['id'], m['name'], self.id) for m in data['models']]
        self.channels = [Channel(c['id'], c['name'], self.id) for c in data['channels']]
        self.channel_interfaces = {c.name: c(self) for c in all_channels if self.has_channel(c.name)}

    ####################################################################################################################
    # CHANNELS
    ####################################################################################################################

    @property
    def slack(self):
        return self.channel_interfaces['slack']

    @property
    def github(self):
        return self.channel_interfaces['github']

    @property
    def twitter(self):
        return self.channel_interfaces['twitter']

    @property
    def github_api(self):
        return g

    # @property
    # def notion_api(self):
    #     return notion_api

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
        self.models = [Model(m['id'], m['name'], self.id) for m in payload['models']]
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
        self.channels = [Channel(c['id'], c['name'], self.id) for c in payload['channels']]
        self.channel_interfaces = {c.name: c for c in all_channels if self.has_channel(c.name)}
        return self.channels

    ####################################################################################################################
    # RUNNING
    ####################################################################################################################

    @staticmethod
    async def handle_healthcheck():
        return {'healthcheck': 'hello world!'}

    async def redirect_dashboard(self):
        return RedirectResponse(
            url=f'{config["admin_url_large"]}#agent_name={self.id.agent_name}'
        )

    async def handle_trigger(self, trigger_input: TriggerInput):
        message = extract_message(trigger_input)
        asyncio.create_task(self.handler(message))
        return {'status': 'success'}

    def start(self, handler: Callable, on_boot: Union[Callable, None] = None, port=8080, channels: List[str] = None,
              models: List[str] = None):
        """Registers and starts the server"""
        # =====[ Registration ]=====
        self.register(channels=channels, models=models)

        # =====[ On Boot ]=====
        if on_boot:
            on_boot()

        # =====[ App setup ]=====
        self.app = app
        self.handler = handler
        router.add_api_route('/', endpoint=self.redirect_dashboard, methods=['GET'])
        router.add_api_route('/healthcheck', endpoint=self.handle_healthcheck, methods=['GET'])
        router.add_api_route('/io', endpoint=self.handle_trigger, methods=['POST'])
        self.app.include_router(router)

        # =====[ Run ]=====
        logging.info('=====[ App info: ]=====')
        logging.info(f'user_name: {self.id.user_name}')
        logging.info(f'agent_name: {self.id.agent_name}')
        logging.info(f'agent_id: {self.id.agent_id}')
        logging.info(f'instance_id: {self.id.instance_id}')
        logging.info(f'app_url: {self.app_url}')
        uvicorn.run(self.app, host="0.0.0.0", port=port)

        # =====[ Print out details ]=====
        logging.info('Startup complete')
        logging.info(f'user_name: {self.id.user_name}')
        logging.info(f'agent_name: {self.id.agent_name}')
        logging.info(f'agent_id: {self.id.agent_id}')
        logging.info(f'instance_id: {self.id.instance_id}')


ai = AI()
