from plone.app.contenttypes.interfaces import IDocument
from plone.app.contenttypes.interfaces import INewsItem
from plone.indexer import indexer


@indexer(INewsItem)
def news_item_has_thumbs(obj):
    """
    Provides a catalog-indexable boolean value
    to mark items that have thumbnail previews
    """
    adapter = obj.unrestrictedTraverse('@@images')
    if not adapter:
        return False
    return not not adapter.getAvailableSizes('image').get('mini')


@indexer(IDocument)
def document_has_thumbs(obj):
    """
    Provides a catalog-indexable boolean value
    to mark items that have thumbnail previews
    """
    adapter = obj.unrestrictedTraverse('@@images')
    if not adapter:
        return False
    return not not adapter.getAvailableSizes('image').get('mini')
