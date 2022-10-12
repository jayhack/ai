import os

def is_local_dev():
    return 'REPL_OWNER' not in os.environ

values = {
    'prod': {
        'server_url': 'https://dev-backend.fly.dev',
        'admin_url': 'https://devai.retool.com/embedded/public/6afe1291-968e-43cd-82bd-5fa267785261',
        'admin_url_large': 'https://devai.retool.com/embedded/public/1c65ff6f-4485-489a-b151-205e635b7f7b'
    },
    'local': {
        'server_url': 'http://localhost:8080',
        'admin_url': 'https://devai.retool.com/embedded/public/6afe1291-968e-43cd-82bd-5fa267785261',
        'admin_url_large': 'https://devai.retool.com/embedded/public/1c65ff6f-4485-489a-b151-205e635b7f7b'
    }
}

config = values['local'] if is_local_dev() else values['prod']
