from Products.Five.browser import BrowserView

from ploneintranet.attachments import utils
from ploneintranet.attachments.attachments import IAttachmentStorage
import logging

log = logging.getLogger(__name__)

try:
    from ploneintranet.docconv.client.interfaces import IPreviewFetcher
except ImportError:
    IPreviewFetcher = None


class UploadAttachments(BrowserView):

    def __call__(self):
        token = self.request.get('attachment-form-token')
        attachments = self.request.get('form.widgets.attachments')
        self.attachments = []
        if attachments:
            temp_attachments = IAttachmentStorage(self.context)
            attachment_objs = utils.extract_attachments(attachments)
            for obj in attachment_objs:
                obj.setId('{0}-{1}'.format(token, obj.getId()))
                temp_attachments.add(obj)
                obj = temp_attachments.get(obj.getId())
                if IPreviewFetcher is not None:
                    try:
                        IPreviewFetcher(obj)()
                    except Exception as e:
                        log.warn('Could not get previews for attachment: {0}, '
                                 '{1}: {2}'.format(
                                     obj.getId(), e.__class__.__name__, e))
                self.attachments.append(obj)
        return self.index()
