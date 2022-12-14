import asyncio
import logging
from typing import Callable
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

from fastapi import APIRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import RedirectResponse

from .app_id import AppID
from .channels.airtable import AirtableChannel
from .channels.channel import Channel, ChannelType
from .channels.create_channel import create_channel, ChannelUnionType
from .channels.gh import GithubChannel
from .channels.slack import SlackChannel
from .channels.twitter import TwitterChannel
from .get_env import get_env
from .utils.api_interface import APIInterface
from .utils.config import config
from .utils.message import Message
from .utils.model import Model

logging.basicConfig(level=logging.INFO)


class ChannelInput(BaseModel):
    id: int
    name: str


class TriggerInput(BaseModel):
    id: int
    timestamp: str
    channel: ChannelInput
    body: Dict


def extract_message(t: TriggerInput) -> Message:
    return Message(
        channel=t.channel.name,
        timestamp=t.timestamp,
        body=dict(t.body)
    )


app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://*.jay.ai",
    "https://gp-tutor.jay.ai",
    'https://*.fly.dev',
    'https://llmusic-backend.fly.dev',
    "https://music.jay.ai",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
router = APIRouter()

default_channels: List[str] = []
default_models: List[str] = ['openai/gpt-3', 'stability-ai/stable-diffusion', 'play.ht', 'assembly.ai']


class AI(APIInterface):
    id: AppID
    app_url: str
    base_url = config['server_url']
    app = None
    handler = None
    channels: List[ChannelUnionType]
    models: List[Model]

    ####################################################################################################################
    # INITIALIZATION
    ####################################################################################################################

    @classmethod
    def get_app_metadata(cls) -> Tuple[str, str, str]:
        """Assumes Replit"""
        env = get_env()
        return env.agent_name, env.user_name, env.app_url

    def __init__(self):
        app_name, user_name, self.app_url = self.get_app_metadata()
        self.base_url = config['server_url'] + '/agents'
        self.id = AppID(
            user_name=user_name,
            agent_name=app_name,
            agent_id=None,
            instance_id=None,
            creds=None
        )
        super(AI, self).__init__(self.id, self.base_url)
        self.app = app

    def register(self, channels: List[str], models: List[str]):
        """Announces presence of this agent to the server"""
        print('Registering agent...')
        print(self.id.agent_name)
        print(self.id.user_name)
        use_channels = channels or default_channels
        use_models = models or default_models
        data = self._post(f'/register', {
            'app_name': self.id.agent_name,
            'user_name': self.id.user_name,
            'url': self.app_url,
            'channels': use_channels,
            'models': use_models
        })
        if not data:
            raise Exception('Could not establish connection to server')
        else:
            if data['is_new']:
                logging.info(f'Registered new agent: {self.id.agent_name}')
            else:
                logging.info(f'Registered returning agent: {self.id.agent_name}')
                print(data)
        self.id.agent_id = data['agent']['id']
        self.id.instance_id = data['instance']['id']
        self.id.creds = data['channels']
        self.models = [Model(m['id'], m['name'], self.id) for m in data['models']]
        self.channels = [create_channel(self.id, c) for c in data['channels']]

    ####################################################################################################################
    # CHANNELS
    ####################################################################################################################
    """
    Should support an API like so:
    ai.twitter.send_message(text)
    ai.get_channel(channel_name).send_message(text) # accounts for multiple twitter accounts
    
    So really these should be returning a Channel object. Can we make the API interfaces subclass Channel?
    """

    def _channel_by_name(self, channel_name: str) -> Channel:
        channels = [c for c in self.channels if c.name == channel_name]
        if len(channels) == 0:
            raise Exception(f'No such channel {channel_name}; Try registering a channel of this type')
        return channels[0]

    def _channel_by_type(self, channel_type: str) -> List[ChannelUnionType]:
        return [c for c in self.channels if c.channel_type == channel_type]

    def _get_first_by_type(self, channel_type: ChannelType) -> ChannelUnionType:
        channels = self._channel_by_type(channel_type)
        if len(channels) == 0:
            raise Exception(f'No such channel of type {channel_type}; Try registering a channel of this type')
        return channels[0]

    @property
    def slack(self) -> SlackChannel:
        c: SlackChannel = self._get_first_by_type('Slack')
        return c

    @property
    def github(self) -> GithubChannel:
        c: GithubChannel = self._get_first_by_type('GitHub')
        return c

    @property
    def twitter(self) -> TwitterChannel:
        c: TwitterChannel = self._get_first_by_type('Twitter')
        return c

    @property
    def airtable(self):
        c: AirtableChannel = self._get_first_by_type('Airtable')
        return c

    @property
    def notion(self):
        raise NotImplementedError

    def get_channel(self, channel_name: str):
        return self._channel_by_name(channel_name)

    def get_channels(self) -> List[Channel]:
        return self.channels

    def has_channel(self, name: str) -> bool:
        return len([c for c in self.channels if c.name == name]) > 0

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
    #
    ####################################################################################################################

    @staticmethod
    async def handle_healthcheck():
        return {'healthcheck': 'hello world!'}

    def get_dashboard_embedded(self) -> str:
        return f'{config["admin_url_large"]}#agent_name={self.id.agent_name}'

    def get_dashboard(self) -> str:
        return config['dashboard_url'].format(agent_name=self.id.agent_name, username=self.id.user_name)

    async def redirect_dashboard(self):
        return RedirectResponse(
            url=f'{config["admin_url_large"]}#agent_name={self.id.agent_name}'
        )

    async def redirect_dashboard_large(self):
        return RedirectResponse(
            url=config["dashboard_url"].format(username=self.id.user_name, agent_name=self.id.agent_name)
        )

    async def handle_trigger(self, trigger_input: TriggerInput):
        if self.handler:
            message = extract_message(trigger_input)
            asyncio.create_task(self.handler(message))
        return {'status': 'success'}

    def setup(self, name='default'):
        self.app = app
        router.add_api_route('/', endpoint=self.redirect_dashboard, methods=['GET'])
        router.add_api_route('/healthcheck', endpoint=self.handle_healthcheck, methods=['GET'])
        router.add_api_route('/io', endpoint=self.handle_trigger, methods=['POST'])
        self.app.include_router(router)
        return self.app

    def start(self, handler: Union[Callable, None] = None, on_boot: Union[Callable, None] = None, port=8080,
              channels: List[str] = None,
              models: List[str] = None):
        """Registers and starts the server"""
        self.register(channels=channels, models=models)
        # =====[ On Boot ]=====
        if on_boot:
            on_boot()

        # =====[ App setup ]=====
        self.app = app
        self.handler = handler
        router.add_api_route('/', endpoint=self.redirect_dashboard, methods=['GET'])
        router.add_api_route('/dashboard', endpoint=self.redirect_dashboard_large, methods=['POST'])
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
        logging.info(f'dashboard: {self.get_dashboard()}')
        # uvicorn.run(self.app, host="0.0.0.0", port=port)

        # =====[ Print out details ]=====
        logging.info('Startup complete')
        logging.info(f'user_name: {self.id.user_name}')
        logging.info(f'agent_name: {self.id.agent_name}')
        logging.info(f'agent_id: {self.id.agent_id}')
        logging.info(f'instance_id: {self.id.instance_id}')
        return self.app


ai = AI()
