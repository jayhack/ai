import os


class Envvars:
    def __init__(self, user_name, agent_name, is_replit, env, app_url):
        self.user_name = user_name
        self.agent_name = agent_name
        self.is_replit = is_replit
        self.env = env
        self.app_url = app_url

    def __repr__(self):
        return f'Envvars({self.user_name}, {self.agent_name}, {self.is_replit}, {self.env}, {self.app_url})'


def get_env():
    user_name = os.environ.get('THOUGHTSPEED_USERNAME')
    agent_name = os.environ.get('THOUGHTSPEED_AGENTNAME')
    is_replit = 'REPL_OWNER' in os.environ
    env = os.environ.get('THOUGHTSPEED_ENV', 'prod')
    if is_replit:
        url = f'https://{agent_name}.{user_name}.repl.co'
    else:
        url = f'https://{agent_name}.fly.dev'
    return Envvars(user_name, agent_name, is_replit, env, url)


def get_agent_url():
    env = get_env()
    if env.is_replit:
        f'https://{env.agent_name}.{env.user_name}.repl.co'
    else:
        return f'https://{env.agent_name}.fly.dev'
