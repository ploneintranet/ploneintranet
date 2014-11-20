from Products.CMFCore.utils import getToolByName
from five import grok
from plone import api
from zope.annotation import IAnnotations
from zope.component.hooks import getSite
from zope.interface import Interface

from ploneintranet.docconv.client.config import (
    PREVIEW_IMAGES_KEY,
    THUMBNAIL_KEY,
    PDF_VERSION_KEY,
    PREVIEW_MESSAGE_KEY,
)
from ploneintranet.docconv.client.async import queueConversionJob

from logging import getLogger

logger = getLogger(__name__)


def initialize(context):
    """Initializer called when used as a Zope 2 product."""


class IDocconv(Interface):
    """ """

    def has_pdf():
        """ """

    def has_previews():
        """ """

    def has_thumbs():
        """ """

    def conversion_message():
        """ """

    def get_pdf():
        """ """

    def get_previews():
        """ """

    def get_thumbs():
        """ """

    def generate_all():
        """ """


class DocconvAdapter(grok.Adapter):
    """ """
    grok.context(Interface)
    grok.provides(IDocconv)

    def __init__(self, context, request=None):
        super(DocconvAdapter, self).__init__(context)
        if request is not None:
            self.request = request
        elif hasattr(context, 'REQUEST'):
            self.request = context.REQUEST
        elif hasattr(context, 'request'):
            self.request = context.request
        else:
            self.request = api.portal.getRequest()
        self._annotations = IAnnotations(self.context)

    def has_pdf(self):
        return is_available(self.context, data_type='pdf')

    def has_previews(self):
        return is_available(self.context, data_type='preview')

    def has_thumbs(self):
        return is_available(self.context, data_type='thumb')

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


def is_autoconv_enabled():
    site = getSite()
    portal_properties = getToolByName(site, 'portal_properties')
    site_properties = portal_properties.site_properties
    return site_properties.getProperty('docconv_autoconv', False)


def get_number_of_pages(obj, img_type='preview'):
    if img_type in [PREVIEW_IMAGES_KEY, THUMBNAIL_KEY]:
        annotation_key = img_type
    elif img_type == 'preview':
        annotation_key = PREVIEW_IMAGES_KEY
    elif img_type == 'thumb':
        annotation_key = THUMBNAIL_KEY
    else:
        return -1
    annotations = IAnnotations(obj)
    if annotation_key in annotations:
        return len(annotations[annotation_key])
    return 0


def is_available(obj, data_type='preview'):
    if data_type == 'pdf':
        annotations = IAnnotations(obj)
        if annotations.get(PDF_VERSION_KEY):
            return True
    if get_number_of_pages(obj, img_type=data_type) > 0:
        return True
    else:
        if is_autoconv_enabled() and hasattr(obj, 'REQUEST'):
            queueConversionJob(obj, obj.REQUEST)
        return False
