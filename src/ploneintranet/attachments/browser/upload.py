from Products.Five.browser import BrowserView
from plone import api
from plone.app.contenttypes.content import File
from plone.app.contenttypes.content import Image
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

    def get_docconv_thumbs_urls(self, attachment):
        '''
        If we have a IDocconv adapted object,
        we ask docconv for thumbs urls
        '''
        docconv = IDocconv(attachment, None)
        if not docconv:
            return []

        pages = docconv.get_number_of_pages()
        if pages <= 0:  # we have no previews when pages is 0 or -1
            return []

        base_url = '%s/docconv_image_thumb.jpg?page=' % (
            attachment.absolute_url()
        )
        return [
            (base_url + str(i+1)) for i in range(pages)
        ]

    def get_image_thumbs_urls(self, image, image_field="image"):
        '''
        If we have an Image or a File object,
        we ask the Plone scale machinery for a URL
        '''
        images = api.content.get_view(
            'images',
            image,
            self.request,
        )
        try:
            urls = [images.scale(image_field, 'preview').absolute_url()]
        except:
            log.exception('Preview url generation failed')
            urls = []
        return urls

    def get_thumbs_urls(self, attachment):
        ''' This will return the URL for the thumbs of the attachment

        '''
        # We first ask docconv for a URL
        urls = self.get_docconv_thumbs_urls(attachment)
        if urls:
            return urls

        # If we have an image we return the usual preview url
        if isinstance(attachment, Image):
            return self.get_image_thumbs_urls(attachment)

        # If we have a file it can contain an image: we try before aborting
        if isinstance(attachment, File):
            return self.get_image_thumbs_urls(attachment, 'file')

        return []

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
