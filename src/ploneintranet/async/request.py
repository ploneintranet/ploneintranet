from zope.component import adapts
from zope.interface import implementer
from zope.publisher.interfaces import IRequest

from ploneintranet.async.interfaces import IAsyncRequest
from ploneintranet.async.celerytasks import dispatch


@implementer(IAsyncRequest)
class AsyncRequest(object):
    """
    Execute a request asynchronously via Celery.

    Extracts authentication credentials from a original request
    and submits a new post request, taking special care
    that all calls are properly serialized.
    """

    adapts(IRequest)  # that is the right one

    def __init__(self, orig_request):
        """Adapt a request to extract credentials."""
        self.request = orig_request
        self.headers = {}
        # Plone auth will be set as '__ac' cookie
        self.cookies = orig_request.cookies
        # Zope basic auth
        if self.request._auth:
            # avoid error: Can't pickle <type 'instancemethod'>
            auth = self.request._auth  # @property?
            self.headers = dict(Authorization=auth)

    def post(self, url, data={}, headers={}, cookies={}):
        """Start a Celery task that will execute a post request.

        The post will call `url` with `self.headers` as request headers,
        `self.cookie` as request cookies, and `data` as post data
        via the python request library.

        Any `headers={}` and `cookies={}` args will be merged with
        the headers and cookies extracted from the original request.

        All arguments should be immutables that can be serialized.
        """
        self.headers.update(headers)
        self.cookies.update(cookies)
        # calling code should handle redis.exceptions.ConnectionError
        return dispatch.delay(url, data, self.headers, self.cookies)
