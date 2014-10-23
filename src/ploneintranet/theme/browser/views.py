from datetime import datetime
from datetime import timedelta
from plone import api
from zExceptions import NotFound
from zope.publisher.browser import BrowserPage
from zope.publisher.browser import BrowserView
from Acquisition import aq_inner


class ExampleDragAndDropUpload(BrowserView):
    """ A view to serve as an example of drag & drop uploading.
    """


class ExampleResourcePolling(BrowserView):
    """ A view to serve as an example of how to use pat-resourcepolling
    """

    def get_images(self):
        catalog = api.portal.get_tool('portal_catalog')
        return catalog(portal_type='Image', path=self.context.getPhysicalPath())


class ExampleFilePreview(BrowserPage):
    """ A view to serve as an example of file previews (e.g. via docconv)
    """

    def __call__(self, *args, **kw):
        context = aq_inner(self.context)
        if not hasattr(context, '_v_wait'):
            context._v_wait = datetime.now() + timedelta(seconds=10)
        if context._v_wait <= datetime.now():
            del context._v_wait
            return self.request.RESPONSE.redirect(context.absolute_url())
        else:
            raise NotFound

