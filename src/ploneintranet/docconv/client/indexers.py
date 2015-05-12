from Products.CMFCore.interfaces import IContentish
from plone.indexer import indexer
from ploneintranet.docconv.client.interfaces import IDocconv


@indexer(IContentish)
def has_thumbs(obj):
    """
    Provides a catalog-indexable boolean value
    to mark items that have thumbnail previews
    """
    return IDocconv(obj).has_thumbs()
