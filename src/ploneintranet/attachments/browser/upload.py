from Products.Five.browser import BrowserView

from ploneintranet.attachments import utils
from ploneintranet.attachments.attachments import IAttachmentStorage
from ploneintranet.docconv.client.interfaces import IDocconv
import logging

log = logging.getLogger(__name__)
try:
    from ploneintranet.docconv.client.interfaces import IPreviewFetcher
except ImportError:
    IPreviewFetcher = None


class UploadAttachments(BrowserView):

    def get_thumbs_urls(self, attachment):
        ''' This will return the URL for the thumbs of the attachment
        '''
        base_url = '%s/docconv_image_thumb.jpg?page=' % (
            attachment.absolute_url()
        )
        thumbs = IDocconv(attachment).get_thumbs()
        return [
            (base_url + str(i+1)) for i, thumb in enumerate(thumbs)
        ]

    def __call__(self):
        token = self.request.get('attachment-form-token')
        attachments = self.request.get('form.widgets.attachments')
        self.attachments = []
        if attachments:
            temp_attachments = IAttachmentStorage(self.context)
            attachment_objs = utils.extract_attachments(attachments)
            for obj in attachment_objs:
                obj.id = '{0}-{1}'.format(token, obj.id)
                temp_attachments.add(obj)
                obj = temp_attachments.get(obj.id)
                if IPreviewFetcher is not None:
                    try:
                        IPreviewFetcher(obj)()
                    except Exception as e:
                        log.warn('Could not get previews for attachment: {0}, '
                                 '{1}: {2}'.format(
                                     obj.id, e.__class__.__name__, e))
                self.attachments.append(obj)

        return self.index()
