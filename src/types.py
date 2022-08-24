"""
TODO: combine this file with the types.py from the client side
"""


class Image(object):
    """Convenient methods for access an image (url/numpy etc.)"""
    url: str
    array: str

    def __init__(self, url=None, array=None):
        self.url = url
        self.array = array

    @classmethod
    def from_url(cls, url):
        return cls(url=url)


class ModelQuery(object):
    """General-purpose model query; enables serialization"""

    def __init__(self, body: dict):
        self.body = body

    def __getitem__(self, item):
        return self.body[item]

    def to_dict(self):
        if type(self.body) is dict:
            d = self.body.copy()
            for k in d.keys():
                if type(d[k]) is Image:
                    d[k] = {
                        '__type': 'Image',
                        'url': d[k].url
                    }
            return {'body': d}
        return {'body': self.body}

    @classmethod
    def from_dict(cls, d):
        d = d['body'].copy()
        for k in d.keys():
            if type(d[k]) is dict:
                if d[k].get('__type') == 'Image':
                    d[k] = Image.from_url(d[k].get('url'))
        return cls(d)
