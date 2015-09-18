from Products.CMFCore.interfaces import IContentish
from plone.indexer import indexer
from ploneintranet.docconv.client.interfaces import IDocconv


@indexer(IContentish)
def has_thumbs(obj):
    """
    Provides a catalog-indexable boolean value
    to mark items that have thumbnail previews
    """
    if IDocconv(obj).has_thumbs():
        return True
    # also check for (lead)image
    if not hasattr(obj, 'image') or not obj.image:
        return False
    adapter = obj.unrestrictedTraverse('@@images')
    if not adapter:
        return False
    return not not adapter.getAvailableSizes('image').get('mini')
