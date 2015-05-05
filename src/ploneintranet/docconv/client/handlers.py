import logging
from plone.app.contenttypes.interfaces import IDocument
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.app.contenttypes.interfaces import ILink
from plone.app.contenttypes.interfaces import INewsItem
from five import grok
from zope.annotation import IAnnotations
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from ploneintranet.attachments.attachments import IAttachmentStoragable
from ploneintranet.attachments.utils import IAttachmentStorage
from ploneintranet.docconv.client.async import queueDelayedConversionJob
from ploneintranet.docconv.client.config import PDF_VERSION_KEY
from ploneintranet.docconv.client.config import PREVIEW_IMAGES_KEY
from ploneintranet.docconv.client.config import PREVIEW_MESSAGE_KEY
from ploneintranet.docconv.client.config import THUMBNAIL_KEY
from ploneintranet.docconv.client.exceptions import ConfigError
from ploneintranet.docconv.client.fetcher import fetchPreviews
from ploneintranet.docconv.client.interfaces import IDocconv

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
    if not IAttachmentStoragable.providedBy(obj):
        return
    attachment_storage = IAttachmentStorage(obj)
    for att_id in attachment_storage.keys():
        docconv = IDocconv(attachment_storage.get(att_id))
        if not docconv.has_thumbs():
            docconv.generate_all()


@grok.subscribe(IDocument, IObjectAddedEvent)
@grok.subscribe(IFile, IObjectAddedEvent)
@grok.subscribe(IImage, IObjectAddedEvent)
@grok.subscribe(ILink, IObjectAddedEvent)
@grok.subscribe(INewsItem, IObjectAddedEvent)
def archetype_added_in_workspace(obj, event):
    _update_preview_images(obj, event)


@grok.subscribe(IDocument, IObjectModifiedEvent)
@grok.subscribe(IFile, IObjectModifiedEvent)
@grok.subscribe(IImage, IObjectModifiedEvent)
@grok.subscribe(ILink, IObjectModifiedEvent)
@grok.subscribe(INewsItem, IObjectModifiedEvent)
def archetype_edited_in_workspace(obj, event):
    _update_preview_images(obj, event)


@grok.subscribe(IAttachmentStoragable, IObjectAddedEvent)
def attachmentstoragable_added(obj, event):
    generate_attachment_preview_images(obj)
