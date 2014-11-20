import logging
from Products.ATContentTypes.interfaces import IATDocument
from Products.ATContentTypes.interfaces import IATFile
from Products.ATContentTypes.interfaces import IATImage
from Products.ATContentTypes.interfaces import IATLink
from Products.ATContentTypes.interfaces import IATNewsItem
from Products.Archetypes.interfaces import IObjectEditedEvent
from Products.Archetypes.interfaces import IObjectInitializedEvent
from five import grok
from plone import api
from zope.annotation import IAnnotations
from zope.app.container.interfaces import IObjectAddedEvent

from ploneintranet.docconv.client import IDocconv
from ploneintranet.docconv.client.async import queueDelayedConversionJob
from ploneintranet.docconv.client.exceptions import ConfigError
from ploneintranet.docconv.client.fetcher import fetchPreviews
from ploneintranet.docconv.client.config import (
    PDF_VERSION_KEY,
    PREVIEW_IMAGES_KEY,
    THUMBNAIL_KEY,
    PREVIEW_MESSAGE_KEY,
)

try:
    from ploneintranet.attachments.attachments import IAttachmentStoragable
    from ploneintranet.attachments.utils import IAttachmentStorage
except ImportError:
    IAttachmentStoragable = None

log = logging.getLogger(__name__)


def _update_preview_images(obj, event):
    annotations = IAnnotations(obj)
    if PREVIEW_IMAGES_KEY in annotations:
        del annotations[PREVIEW_IMAGES_KEY]
    if THUMBNAIL_KEY in annotations:
        del annotations[THUMBNAIL_KEY]
    if PDF_VERSION_KEY in annotations:
        del annotations[PDF_VERSION_KEY]
    if PREVIEW_MESSAGE_KEY in annotations:
        del annotations[PREVIEW_MESSAGE_KEY]
    success = queueDelayedConversionJob(obj, obj.REQUEST)
    if not success:
        try:
            fetchPreviews(obj)
        except ConfigError as e:
            log.error('ConfigError: %s' % e)
    generate_attachment_preview_images(obj)


def generate_attachment_preview_images(obj):
    if (IAttachmentStoragable is not None and
            IAttachmentStoragable.providedBy(obj)):
        attachment_storage = IAttachmentStorage(obj)
        for att_id in attachment_storage.keys():
            docconv = IDocconv(attachment_storage.get(att_id))
            if not docconv.has_thumbs():
                docconv.generate_all()


@grok.subscribe(IATDocument, IObjectInitializedEvent)
@grok.subscribe(IATFile, IObjectInitializedEvent)
@grok.subscribe(IATImage, IObjectInitializedEvent)
@grok.subscribe(IATLink, IObjectInitializedEvent)
@grok.subscribe(IATNewsItem, IObjectInitializedEvent)
def archetype_added_in_workspace(obj, event):
    _update_preview_images(obj, event)


@grok.subscribe(IATDocument, IObjectEditedEvent)
@grok.subscribe(IATFile, IObjectEditedEvent)
@grok.subscribe(IATImage, IObjectEditedEvent)
@grok.subscribe(IATLink, IObjectEditedEvent)
@grok.subscribe(IATNewsItem, IObjectEditedEvent)
def archetype_edited_in_workspace(obj, event):
    _update_preview_images(obj, event)


@grok.subscribe(IAttachmentStoragable, IObjectAddedEvent)
def attachmentstoragable_added(obj, event):
    generate_attachment_preview_images(obj)
