# 🌈
values = {
    'test': {
        'server_url': 'https://localhost:8080',

        'admin_url_large': 'https://devai.retool.com/embedded/public/1c65ff6f-4485-489a-b151-205e635b7f7b',
        'dashboard_url': 'https://devai.retool.com/apps/d51f60a0-23de-11ed-9739-07558902a7b8/Dev%20App#username={username}&agent_name={agent_name}',
    },
    'prod': {
        'server_url': 'https://dev-backend.fly.dev',
        'admin_url_large': 'https://devai.retool.com/embedded/public/1c65ff6f-4485-489a-b151-205e635b7f7b',
        'dashboard_url': 'https://devai.retool.com/apps/d51f60a0-23de-11ed-9739-07558902a7b8/Dev%20App#username={username}&agent_name={agent_name}',
    },
    'local': {
        'server_url': 'http://localhost:8080',
        'admin_url_large': 'https://devai.retool.com/embedded/public/1c65ff6f-4485-489a-b151-205e635b7f7b',
        'dashboard_url': 'https://devai.retool.com/apps/d51f60a0-23de-11ed-9739-07558902a7b8/Dev%20App#username={username}&agent_name={agent_name}',
    }
}

# config = values['local'] if is_local_dev() else values['prod']
from ..get_env import get_env

envvars = get_env()
config = values[envvars.env]
