class APIClientWrapper(object):
    api: any
    _post: callable

    def __init__(self, api: any, _post: callable):
        self.api = api
        self._post = _post
        
    def __getattr__(self, item):
        """returns a callable that then gets logged (?)"""
        def writer_func(*args, **kwargs):
            self._post('/log-action', {
                'method': item,
                'channel': None,
                'args': args,
                'kwargs': kwargs
            })
            self.api.__getattribute__(item)(*args, **kwargs)
        return writer_func
