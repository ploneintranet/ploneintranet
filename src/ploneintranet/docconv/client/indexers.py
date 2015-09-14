from Products.CMFCore.interfaces import IContentish
from plone.indexer import indexer
from ploneintranet import api as pi_api


@indexer(IContentish)
def has_thumbs(obj):
    """
    Provides a catalog-indexable boolean value
    to mark items that have thumbnail previews
    """
    if pi_api.previews.has_previews(obj):
        return True
    # also check for (lead)image
    if not hasattr(obj, 'image') or not obj.image:
        return False
    adapter = obj.unrestrictedTraverse('@@images')
    if not adapter:
        return False
    return not not adapter.getAvailableSizes('image').get('mini')
