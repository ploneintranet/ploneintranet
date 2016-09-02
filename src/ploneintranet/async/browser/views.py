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

    # Additional parameters to be shown in the form, needs to be set by
    # the concrete subclass.
    # This must be a list of dict entries with keys `name` and `type`.
    # Each entry will cause an input field with that type and name to
    # be displayed in the form.
    ADDITIONAL_PARAMETERS = []

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
            if 'attributes' in self.request:
                attributes = self.request['attributes']
                self.context.reindexObject(idxs=attributes)
            else:
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
        return self.template()


class GeneratePDFView(AbstractAsyncView):
    """
    Generate a PDF for the current object
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
            pi_api.previews.generate_pdf(self.context)
        return self.template()
