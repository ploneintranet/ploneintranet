from Products.CMFCore.interfaces import IContentish
from plone.indexer import indexer


@indexer(IContentish)
def has_thumbs(obj):
    """
    Provides a catalog-indexable boolean value
    to mark items that have thumbnail previews
    """
    # TODO: check if the object has any thumbs
    # This was impemented using the now gone IDocconv abstraction layer
