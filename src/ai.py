import asyncio
from typing import Dict
from typing import List

import uvicorn
from fastapi import APIRouter
from fastapi import FastAPI
from pydantic import BaseModel

from .api_interface import APIInterface
from .channel import Channel
from .channels.slack import ChannelInterface, SlackChannel
from .config import config
from .message import Message
from .model import Model

all_channels = [SlackChannel]


class ChannelInput(BaseModel):
    id: int
    name: str


class MessageBody(BaseModel):
    text: str


class TriggerInput(BaseModel):
    id: int
    timestamp: str
    channel: ChannelInput
    producer_id: int
    body: MessageBody


def extract_message(t: TriggerInput) -> Message:
    return Message(
        channel=t.channel.name,
        timestamp=t.timestamp,
        body=dict(t.body)
    )


app = FastAPI()
router = APIRouter()


@app.get('/healthcheck')
async def healthcheck():
    return {'healthcheck': 'hello world!'}


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

    def init(self, name):
        self.name = name
        self.base_url = f'{config["server_url"]}/agents/{self.name}'
        self._register()

    def _register(self):
        data = self._get(f'/register')
        if not data:
            raise Exception('Could not establish connection to server')
        self.id = data['agent']['id']
        self.models = [Model(m['id'], m['name'], self.name) for m in data['models']]
        self.channels = [Channel(c['id'], c['name'], self.name) for c in data['channels']]
        self.channel_interfaces = {c.name: c(self) for c in all_channels if self.has_channel(c.name)}

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

    # def __getattr__(self, item: str):
    #     """allows for syntax like ai.slack.send_message"""
    #     if self.has_channel(item):
    #         return self.channel_interfaces[item]
    #     return None

    ####################################################################################################################
    # MESSAGES
    ####################################################################################################################

    def send_message(self, channel_name: str, payload: dict):
        if not self.has_channel(channel_name):
            raise Exception(f'Invalid channel: {channel_name}')
        channel = self.get_channel(channel_name)
        response = self._post('/message', {
            'channel_name': channel.name,
            'channel_id': channel.id,
            'channel': channel.__dict__(),
            'payload': dict(payload)
        })
        if response is not None:
            print(f'Successfully sent message: {dict(payload)}')
        return response

    ####################################################################################################################
    # RUNNING
    ####################################################################################################################

    async def handle_trigger(self, input: TriggerInput):
        message = extract_message(input)
        print('Before created task')
        asyncio.create_task(self.handler(message))
        print('After created task')
        return {'status': 'success'}

    def start(self, handler, port=8080):
        self.app = app
        self.handler = handler
        router.add_api_route('/io', endpoint=self.handle_trigger, methods=['POST'])
        self.app.include_router(router)
        uvicorn.run(self.app, host="0.0.0.0", port=port)


ai = AI()
