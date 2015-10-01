import logging
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ploneintranet import api as pi_api

logger = logging.getLogger(__name__)


class AbstractAsyncView(BrowserView):
    """
    Class to be used for browser views executing tasks called by async.
    """
    template = ViewPageTemplateFile('templates/protected.pt')

    def authenticated(self):
        return self.request.get('_authenticator', False)


class ReindexObjectView(AbstractAsyncView):
    """
    Reindex the current object
    """

    def __call__(self):
        """
        Execute the actual reindex.
        The ploneintranet.async framework provides a plone.protect
        authenticator automatically.
        For manual testing, render a simple form to provide the
        authenticator.
        Please do not disable CSRF protection.
        """
        if self.authenticated():
            logger.info("Reindexing %s", self.context.absolute_url(1))
            self.context.reindexObject()
        return self.template()


class GeneratePreviewsView(AbstractAsyncView):
    """
    Generate Previews for the current object
    """

    def __call__(self):
        """
        Execute the preview generation.
        The ploneintranet.async framework provides a plone.protect
        authenticator automatically.
        For manual testing, render a simple form to provide the
        authenticator.
        Please do not disable CSRF protection.
        """
        if self.authenticated():
            logger.info("Generating previews for %s",
                        self.context.absolute_url(1))
            pi_api.previews.generate_previews(self.context)
            self.context.reindexObject()
        return self.template()
