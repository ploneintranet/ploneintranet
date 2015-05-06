from plone import api
from zope.annotation import IAnnotations

from ploneintranet.docconv.client import is_autoconv_enabled
from ploneintranet.docconv.client.async import queueConversionJob
from ploneintranet.docconv.client.config import PDF_VERSION_KEY
from ploneintranet.docconv.client.config import PREVIEW_IMAGES_KEY
from ploneintranet.docconv.client.config import PREVIEW_MESSAGE_KEY
from ploneintranet.docconv.client.config import THUMBNAIL_KEY


class DocconvAdapter(object):
    """ """

    def __init__(self, context, request=None):
        self.context = context
        if request is not None:
            self.request = request
        elif hasattr(context, 'REQUEST'):
            self.request = context.REQUEST
        elif hasattr(context, 'request'):
            self.request = context.request
        else:
            self.request = api.portal.getRequest()
        self._annotations = IAnnotations(self.context)

    def get_number_of_pages(self, img_type='preview'):
        if img_type in [PREVIEW_IMAGES_KEY, THUMBNAIL_KEY]:
            annotation_key = img_type
        elif img_type == 'preview':
            annotation_key = PREVIEW_IMAGES_KEY
        elif img_type == 'thumb':
            annotation_key = THUMBNAIL_KEY
        else:
            return -1
        annotations = IAnnotations(self.context)
        if annotation_key in annotations:
            return len(annotations[annotation_key])
        return 0

    def is_available(self, data_type='preview'):
        if data_type == 'pdf':
            annotations = IAnnotations(self.context)
            if annotations.get(PDF_VERSION_KEY):
                return True
        if self.get_number_of_pages(img_type=data_type) > 0:
            return True
        else:
            if is_autoconv_enabled() and hasattr(self.context, 'REQUEST'):
                queueConversionJob(self.context, self.context.REQUEST)
            return False

    def has_pdf(self):
        return self.is_available(data_type='pdf')

    def has_previews(self):
        return self.is_available(data_type='preview')

    def has_thumbs(self):
        return self.is_available(data_type='thumb')

    def conversion_message(self):
        if PREVIEW_MESSAGE_KEY in self._annotations:
            return self._annotations[PREVIEW_MESSAGE_KEY]
        return ''

    def _get_data(self, key):
        data = self._annotations.get(key)
        if not data and is_autoconv_enabled():
            self.generate_all()
        return data

    def get_pdf(self):
        return self._get_data(PDF_VERSION_KEY)

    def get_previews(self):
        return self._get_data(PREVIEW_IMAGES_KEY)

    def get_thumbs(self):
        return self._get_data(THUMBNAIL_KEY)

    def generate_all(self):
        return queueConversionJob(self.context, self.request)
