# coding=utf-8
from .case import ICase
from datetime import datetime
from plone.app.contenttypes.interfaces import IDocument
from plone.app.contenttypes.interfaces import IEvent
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.app.contenttypes.interfaces import ILink
from plone.app.contenttypes.interfaces import INewsItem
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import datify
from plone.indexer.decorator import indexer
from ploneintranet.workspace.workspacefolder import IWorkspaceFolder
from utils import guess_mimetype
from .browser.event import get_invitee_details
from plone.event.interfaces import IEventAccessor


@indexer(IDocument)
def mimetype_document(obj, **kw):
    return obj.format


@indexer(IFile)
def mimetype_file(obj, **kw):
    if hasattr(obj, 'file') and hasattr(obj.file, 'filename'):
        mimetype = guess_mimetype(obj.file.filename)
        if mimetype.strip():
            return mimetype
    return 'application/octet-stream'


@indexer(IImage)
def mimetype_image(obj, **kw):
    if hasattr(obj, 'image') and hasattr(obj.image, 'filename'):
        mimetype = guess_mimetype(obj.image.filename)
        if mimetype.strip():
            return mimetype
    return 'application/octet-stream'


@indexer(ILink)
def mimetype_link(obj, **kw):
    return 'text/x-uri'


@indexer(INewsItem)
def mimetype_newsitem(obj, **kw):
    return 'message/news'


@indexer(IDexterityContent)
def due_dexterity(obj):
    """
    dummy to prevent indexing child objects
    """
    raise AttributeError("This field should not indexed here!")


@indexer(ICase)
def due_case(obj):
    """
    :return: value of field due for cases
    """
    date = getattr(obj, 'due', None)
    date = datify(date)
    return date is None and datetime.max or date


@indexer(IDexterityContent)
def is_division_dexterity(obj):
    """
    dummy to prevent indexing child objects
    """
    raise AttributeError("This field should not indexed here!")


@indexer(IWorkspaceFolder)
def is_division(obj, **kw):
    """Indexes if this object represents a division"""
    return getattr(obj, 'is_division', False)


@indexer(IDexterityContent)
def is_archived_dexterity(obj):
    """
    The default search query is for all items which haven't been archived
    """
    return False


@indexer(IWorkspaceFolder)
def is_archived(obj, **kw):
    """Indexes if this object is not archived

    Return False both when a workspace has no 'archival_date' attribute, and
    also when it is set to None.
    """
    return bool(getattr(obj, 'archival_date'))


@indexer(IDexterityContent)
def division_dexterity(obj):
    """
    dummy to prevent indexing child objects
    """
    raise AttributeError("This field should not indexed here!")


@indexer(IWorkspaceFolder)
def division(obj, **kw):
    """Indexes the division UID if present

    Since this index is a UUIDIndex it needs to return either a UID or None
    """
    return getattr(obj, 'division', None) or None


@indexer(IEvent)
def invitees(obj, **kw):
    """Indexes the invitees as a list"""
    details = get_invitee_details(obj)
    return [x['uid'] for x in details]


@indexer(IEvent)
def whole_day(obj, **kw):
    """ Indexes if this a whole day event """
    return IEventAccessor(obj).whole_day


@indexer(IWorkspaceFolder)
def ws_type_workspace(obj, **kw):
    """Indexes the type of this workspace for marking"""
    return getattr(obj, 'ws_type', 'workspace')


@indexer(IEvent)
def ws_type_event(obj, **kw):
    """Indexes the type of this event based on the workspace it is contained in
       for marking in the calendar"""
    return getattr(obj, 'ws_type', 'workspace')


@indexer(IEvent)
def location(obj, **kw):
    """Indexes the location"""
    return IEventAccessor(obj).location
