import logging


log = logging.getLogger(__name__)


class LogRequestHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        for key, value in request.environ.items():
            if key.startswith('HTTP_'):
                log.info(f'{key[5:].lower():<25}: {value!r}')

        return self.get_response(request)
