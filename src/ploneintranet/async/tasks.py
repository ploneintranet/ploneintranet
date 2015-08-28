"""
Convenience wrappers for Celery tasks providing async jobs for Plone Intranet.

These wrappers provide authentication and serialization for easy calling.

If you want to add a task, add the business logic here, create a celery
task hook in ploneintranet.async.celerytasks and point to that task in your
own task class.
"""
import logging
from zope.component import getMultiAdapter
from zope.interface import implementer

from ploneintranet.async.interfaces import IAsyncTask
from ploneintranet.async import celerytasks

logger = logging.getLogger(__name__)


@implementer(IAsyncTask)
class Post(object):
    """
    Execute a HTTP POST request asynchronously via Celery.

    Extracts authentication credentials from a original request
    and submits a new post request, taking special care
    that all calls are properly serialized.

    Sets a `X-celery-task-name` http header for task request routing
    in HAProxy etc. YMMV.

    This task is suitable as a base class for more specialized
    subclasses. It is structured as if it were an adapter but
    it is not registered or used as an adapter.

    Example usage::

      url = '@@async-checktask'
      data = dict(checksum=random.random())
      try:
          post = Post(self.context, self.request)  # __init__
          post(url, data)                          # __call__
      except redis.exceptions.ConnectionError:
          return self.fail("post", "redis not available")
    """

    task = celerytasks.post

    def __init__(self, context, request):
        """Extract credentials."""
        self.context = context
        self.request = request
        self.headers = {'X-celery-task-name': self.task.name}

        # Plone auth will be set as '__ac' cookie
        self.cookies = request.cookies
        # Zope basic auth
        if self.request._auth:
            # avoid error: Can't pickle <type 'instancemethod'>
            auth = self.request._auth  # @property?
            self.headers['Authorization'] = auth

        # we need context and request for CSRF protection
        authenticator = getMultiAdapter((self.context, self.request),
                                        name=u"authenticator")
        self.data = {'_authenticator': authenticator.token()}
        self.url = self.context.absolute_url()

    def __call__(self, url=None, data={}, headers={}, cookies={}, **kwargs):
        """Start a Celery task that will execute a post request.

        The optional `url` argument may be used to override `self.url`.
        The optional `data`, `headers` and `cookies` args will update
        the corresponding self.* attributes.

        `self.task.apply_async` will called with the self.* attributes
        as arguments and is expected to call `url` with
        `self.headers` as request headers,
        `self.cookie` as request cookies, and `self.data` as post data
        via the python request library.

        `**kwargs` will be passed through as arguments to celery
        `apply_async` so you can set async execution options like
        `countdown`, `expires` or `eta`.

        Returns a <class 'celery.result.AsyncResult'> when running async,
        or a <class 'celery.result.EagerResult'> when running in sync mode.
        """
        if url:
            self.url = url
        if not self.url.startswith('http'):
            self.url = "%s/%s" % (self.context.absolute_url(), url)
        self.data.update(data)
        self.headers.update(headers)
        self.cookies.update(cookies)
        logger.info("Calling %s(%s, ...)", self.task.name, url)
        # calling code should handle redis.exceptions.ConnectionError
        return self.task.apply_async(
            (self.url, self.data, self.headers, self.cookies),
            **kwargs)


@implementer(IAsyncTask)
class GeneratePreview(Post):
    """
    Make an HTTP request to the DocConv Plone instance to generate a preview
    for the given object URL and add it to the object.

    Usage::

      from ploneintranet.async.tasks import GeneratePreview
      GeneratePreview(self.context, self.request)()

    Mind the final call parentheses.

    Of course this depends on the @@generate-previews view being available
    to do the actual heavy lifting. This task only delegates to that
    view via Celery.
    """

    task = celerytasks.generate_and_add_preview

    def __call__(self, url=None, data={}, headers={}, cookies={}, **kwargs):
        if not url:
            url = self.context.absolute_url()
        data.update({
            'action': 'add',
            'url': url
        })
        url += '/@@generate-previews'
        super(GeneratePreview, self).__call__(
            url, data, headers, cookies, **kwargs)
