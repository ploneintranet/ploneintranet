from zope.interface import Interface, Attribute


class IPloneintranetAsyncLayer(Interface):
    """Marker interface that defines a Zope 3 browser layer."""


class IAsyncTask(Interface):
    """
    Execute a request asynchronously via Celery.

    Extracts authentication credentials from a original request
    and submits a new post request, taking special care
    that all calls are properly serialized.
    """

    task = Attribute(
        """A Celery @app.task callable"""
    )

    url = Attribute(
        """A url to be called, relative to self.context.absolute_url()"""
    )

    data = Attribute(
        """A dictionary with request cookie key: value pairs"""
    )

    headers = Attribute(
        """A dictionary with request header key: value pairs"""
    )

    cookies = Attribute(
        """A dictionary with request cookie key: value pairs"""
    )

    def __init__(context, request):
        """
        Initialize the task preprocessor.

        Extracts target url and authentication from the current
        context and url.

        :param context: Current context for the calling view.
        :type context: A Plone object

        :param request: Current request for the calling view.
        """

    def __call__(url=None, data={}, headers={}, cookies={}, **kwargs):
        """Start a Celery task that will execute a post request.

        The optional `url` argument may be used to override `self.url`.
        The optional `data`, `headers` and `cookies` args will update
        the corresponding self.* attributes.

        `self.task.apply_async` will be called
        and is expected to call `url` with
        `self.headers` as request headers,
        `self.cookie` as request cookies, and `self.data` as post data
        via the python request library.

        `**kwargs` will be passed through as arguments to celery
        `apply_async` so you can set async execution options like
        `countdown`, `expires` or `eta`.

        All arguments should be immutables that can be serialized.
        """
