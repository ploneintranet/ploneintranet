from Acquisition import aq_inner
from datetime import datetime
from datetime import timedelta
from plone import api
from zExceptions import NotFound
from zope.publisher.browser import BrowserPage
from zope.publisher.browser import BrowserView
import logging

log = logging.getLogger(__name__)


class Mixin(object):

    def get_images(self):
        catalog = api.portal.get_tool('portal_catalog')
        return catalog(portal_type='Image', path=self.context.getPhysicalPath())


class ExampleDragAndDropUpload(BrowserView):
    """ A view to serve as an example of drag & drop uploading.
    """


class ExampleResourcePolling(BrowserView, Mixin):
    """ A view to serve as an example of how to use pat-resourcepolling
    """


class ExampleEqualiser(BrowserView, Mixin):
    """ A view to illustrate the usage of pat-equaliser, particularly the
        slow loading of images, in order to fix the following bug:

        https://github.com/Patternslib/Patterns/issues/383
    """


class ExampleFilePreview(BrowserPage):
    """ A view to serve as an example of file previews (e.g. via docconv)
    """

    def __call__(self, *args, **kw):
        seconds = 10;
        context = aq_inner(self.context)
        if not hasattr(context, '_v_wait'):
            context._v_wait = datetime.now() + timedelta(seconds=seconds)
            log.info("Set waiting time to %s seconds" % seconds)
        if context._v_wait <= datetime.now():
            log.info("Waiting time exceeded, resetting.")
            del context._v_wait
            return self.request.RESPONSE.redirect(context.absolute_url())
        else:
            log.info("Waiting time not yet exceeded.")
            raise NotFound
