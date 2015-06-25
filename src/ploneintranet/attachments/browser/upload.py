import logging

from Products.Five.browser import BrowserView
from plone.memoize.view import memoize

from ploneintranet import api as pi_api

log = logging.getLogger(__name__)


class UploadAttachments(BrowserView):
    attachments = []

    @property
    @memoize
    def fallback_thumbs_urls(self):
        """ Return a dummy image thumbnails
        """
        return [pi_api.previews.fallback_image_url()]

    def __call__(self):
        """Attach any new attachments to the context and render the preview
        thumbnails
        """
        uploaded_attachments = self.request.get('form.widgets.attachments', [])
        if not isinstance(uploaded_attachments, list):
            uploaded_attachments = [uploaded_attachments]
        for file_field in uploaded_attachments:
            pi_api.attachments.add(
                self.context,
                file_field.filename,
                file_field.read())
        current_attachments = pi_api.attachments.get_attachments(self.context)
        for att in current_attachments:
            self.attachments.append(
                pi_api.previews.get_thumbnail_url(att)
            )
        return self.index()


class UploadStatusAttachments(UploadAttachments):
    """Separate class since it handles permissions differently"""
