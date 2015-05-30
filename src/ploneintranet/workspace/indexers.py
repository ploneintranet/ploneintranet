from plone.app.contenttypes.interfaces import IDocument
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.app.contenttypes.interfaces import ILink
from plone.app.contenttypes.interfaces import INewsItem
from plone.indexer.decorator import indexer
from utils import guess_mimetype


@indexer(IDocument)
def mimetype_document(object, **kw):
    return object.format


@indexer(IFile)
def mimetype_file(object, **kw):
    if hasattr(object, 'file') and hasattr(object.file, 'filename'):
        return guess_mimetype(object.file.filename)
    return 'application/octet-stream'


@indexer(IImage)
def mimetype_image(object, **kw):
    if hasattr(object, 'image') and hasattr(object.image, 'filename'):
        return guess_mimetype(object.image.filename)
    return 'application/octet-stream'


@indexer(ILink)
def mimetype_link(object, **kw):
    return 'text/x-uri'


@indexer(INewsItem)
def mimetype_newsitem(object, **kw):
    return 'message/news'
