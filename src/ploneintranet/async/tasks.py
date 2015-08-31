"""
Convenience wrappers for Celery tasks providing async jobs for Plone Intranet.

These wrappers provide authentication and serialization for easy calling.

If you want to add a task, add the business logic here, create a celery
task hook in ploneintranet.async.celerytasks and point to that task in your
own task class.
"""
import logging
from zope.interface import implementer

from ploneintranet.async.interfaces import IAsyncTask
from ploneintranet.async import celerytasks
from ploneintranet.async.core import AbstractPost

logger = logging.getLogger(__name__)


@implementer(IAsyncTask)
class Post(AbstractPost):
    """
    Execute a HTTP POST request asynchronously via Celery.
    See core.AbstractPost for implementation specifics.

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
    url = None


@implementer(IAsyncTask)
class GeneratePreview(AbstractPost):
    """
    Make an HTTP request to the DocConv Plone instance to generate a preview
    for the given object URL and add it to the object.

    Usage::

      from ploneintranet.async.tasks import GeneratePreview
      GeneratePreview(self.context, self.request)()

    Mind the final call parentheses.

    INCOMPLETE:  @@generate-previews view needs to be implemented.
    """

    task = celerytasks.generate_and_add_preview
    url = '/@@generate-previews'


@implementer(IAsyncTask)
class ReindexObject(AbstractPost):
    """Reindex an object asynchronously.

    Usage:

      from ploneintranet.async.tasks import ReindexObject
      ReindexObject(self.context, self.request)()

    Mind the final call parentheses.
    """

    task = celerytasks.reindex_object
    url = '/@@reindex_object'
