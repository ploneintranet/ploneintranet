from Products.ATContentTypes.interfaces import IATDocument
from Products.ATContentTypes.interfaces import IATFile
from Products.ATContentTypes.interfaces import IATImage
from Products.ATContentTypes.interfaces import IATLink
from Products.ATContentTypes.interfaces import IATNewsItem
from Products.Archetypes.interfaces import IObjectEditedEvent
from Products.Archetypes.interfaces import IObjectInitializedEvent
from five import grok
from zope.annotation import IAnnotations

from ploneintranet.docconv.client.async import queueDelayedConversionJob
from ploneintranet.docconv.client.fetcher import fetchPreviews
from ploneintranet.docconv.client.config import (
    PDF_VERSION_KEY,
    PREVIEW_IMAGES_KEY,
    THUMBNAIL_KEY,
    PREVIEW_MESSAGE_KEY,
)


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
        fetchPreviews(obj)


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
