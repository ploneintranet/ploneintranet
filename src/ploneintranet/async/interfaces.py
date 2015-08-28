from zope.interface import Interface, Attribute


class IPloneintranetAsyncLayer(Interface):
    """Marker interface that defines a Zope 3 browser layer."""


class IAsyncRequest(Interface):
    """
    Execute a request asynchronously via Celery.

    Extracts authentication credentials from a original request
    and submits a new post request, taking special care
    that all calls are properly serialized.
    """

    headers = Attribute(
        """A dictionary with request header key: value pairs"""
    )

    cookies = Attribute(
        """A dictionary with request cookie key: value pairs"""
    )

    def async(task, url, data={}, headers={}, cookies={}, **kwargs):
        """Start a Celery task that will execute a post request.

        `task.apply_async` will called with the rest of the arguments and
        is expected to call `url` with `self.headers` as request headers,
        `self.cookie` as request cookies, and `data` as post data
        via the python request library.

        Any `headers={}` and `cookies={}` args will be merged with
        the headers and cookies extracted from the original request.

        `**kwargs` will be passed through as arguments to celery
        `apply_async` so you can set async execution options like
        `countdown`, `expires` or `eta`.

        All arguments should be immutables that can be serialized.
        """
