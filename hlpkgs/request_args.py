from .snippet import T2I

class RequestArgs:
    def __init__(self, request):
        self._request = request
        self._args = {}

    async def parse(self):
        self._args.update(self._request.)
        if self._request.method in ['POST', 'PUT']:
            content_type = self._request.headers.get('Content-Type', None)
            if content_type.startswith('application/json'):
                args = await self._request.json()
                self._args.update(args)
            elif content_type.startswith('application/x-www-form-urlencoded'):
                text = await self._request.text()
                args = dict(v.split('=') for v in text.split('&'))
                self._args.update(args)
               

    def get(self, key, default=None):
        value = self._request.query.get(key, None)
        if value is None:
            value = self._args.get(key, None)
        return default if value is None else value

    def number(self, key, default=None, valuetype=int):
        value = self._request.query.get(key, None)
        if value is None:
            value = self._args.get(key, None)
        return TextToValue(valuetype, value, default)


__all__ = ['RequestArgs']

