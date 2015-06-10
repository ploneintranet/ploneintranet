import logging

from Products.Five.browser import BrowserView
from plone import api
from plone.memoize.view import memoize
from plone.app.contenttypes.content import File
from plone.app.contenttypes.content import Image

from ploneintranet import api as pi_api

log = logging.getLogger(__name__)


class UploadAttachments(BrowserView):

    @property
    @memoize
    def fallback_thumbs_urls(self):
        """ Return a dummy image thumbnails

        BBB: Ask for a better image :)
        See #122
        """
        url = '/'.join((
            api.portal.get().absolute_url(),
            '++theme++ploneintranet.theme/generated/media/logo.svg'
        ))
        return [url]

    def get_docconv_thumbs_urls(self, attachment):
        """Returns the URLs of all the rendered pages of the document.
        """
        # TODO: actually implement this.
        # The previous implementation relied heavily
        # on the IDocconv abstraction layer
        # which is now gone after async refactoring.
        return []

    def get_image_thumbs_urls(self, image):
        """
        If we have an Image or a File object,
        we ask the Plone scale machinery for a URL
        """
        images = api.content.get_view(
            'images',
            image,
            self.request,
        )
        try:
            urls = [images.scale(scale='preview').absolute_url()]
        except:
            log.error('Preview url generation failed')
            urls = []
        return urls

    def get_thumbs_urls(self, attachment):
        """ This will return the URL for the thumbs of the attachment

        """
        # We first ask docconv for a URL
        urls = self.get_docconv_thumbs_urls(attachment)
        if urls:
            return urls

        # If we have an image we return the usual preview url
        if isinstance(attachment, (Image, File)):
            urls = self.get_image_thumbs_urls(attachment)
        if urls:
            return urls

        # If every other method fails return a fallback
        return self.fallback_thumbs_urls

    def __call__(self):
        uploaded_attachments = self.request.get('form.widgets.attachments')
        if not uploaded_attachments:
            return self.index()

        for file_field in uploaded_attachments:
            pi_api.attachments.add(
                self.context,
                file_field.filename,
                file_field.read())

        return self.index()


class UploadStatusAttachments(UploadAttachments):
    """Separate class since it handles permissions differently"""
