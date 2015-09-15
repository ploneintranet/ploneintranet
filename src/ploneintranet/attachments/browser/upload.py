from Products.Five.browser import BrowserView
from plone import api
from plone.memoize.view import memoize
from plone.app.contenttypes.content import File
from plone.app.contenttypes.content import Image
from plone.i18n.normalizer.interfaces import IURLNormalizer
from ploneintranet import api as pi_api
from ploneintranet.attachments import utils
from ploneintranet.attachments.attachments import IAttachmentStorage
from ploneintranet.docconv.client.handlers import handle_file_creation
from collective.documentviewer.settings import Settings
from zope.component import getUtility
import logging


log = logging.getLogger(__name__)


class UploadAttachments(BrowserView):

    @property
    @memoize
    def fallback_thumbs_urls(self):
        ''' Return a dummy image thumbnails

        BBB: Ask for a better image :)
        See #122
        '''
        return [pi_api.previews.fallback_image_url(api.portal.get())]

    def get_file_thumbs_urls(self, attachment):
        '''
        thumbs provided by c.dv. Only returning the front page.
        '''
        settings = Settings(attachment)
        if settings.successfully_converted is not True:
            return None
        return [attachment.absolute_url() + '/small']

    def get_image_thumbs_urls(self, image):
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
            urls = [images.scale(scale='preview').absolute_url()]
        except:
            log.error('Preview url generation failed')
            urls = []
        return urls

    def get_thumbs_urls(self, attachment):
        ''' This will return the URL for the thumbs of the attachment

        '''
        # We first ask pi_api for a URL
        # This returns previews for images and files
        urls = self.get_file_thumbs_urls(attachment)
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
        token = self.request.get('attachment-form-token')
        uploaded_attachments = self.request.get('form.widgets.attachments')
        if not uploaded_attachments:
            return self.index()

        normalizer = getUtility(IURLNormalizer)
        self.attachments = []
        attachments = IAttachmentStorage(self.context)

        attachment_objs = utils.extract_attachments(uploaded_attachments)
        for obj in attachment_objs:
            obj.id = normalizer.normalize(u'{0}-{1}'.format(token, obj.id))
            attachments.add(obj)
            obj = attachments.get(obj.id)
            try:
                handle_file_creation(obj, None)
            except Exception as e:
                log.warn('Could not get previews for attachment: {0}, '
                         u'{1}: {2}'.format(
                             obj.id, e.__class__.__name__, e))
            self.attachments.append(obj)

        return self.index()


class UploadStatusAttachments(UploadAttachments):
    """Separate class since it handles permissions differently"""
