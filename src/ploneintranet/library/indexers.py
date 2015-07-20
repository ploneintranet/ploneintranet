from plone.app.contenttypes.interfaces import IDocument
from plone.app.contenttypes.interfaces import INewsItem
from plone.indexer import indexer


@indexer(INewsItem)
def news_item_has_thumbs(obj):
    """
    Provides a catalog-indexable boolean value
    to mark items that have thumbnail previews
    """
    if not hasattr(obj, 'image') or not obj.image:
        return False
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
    if not hasattr(obj, 'image') or not obj.image:
        return False
    adapter = obj.unrestrictedTraverse('@@images')
    if not adapter:
        return False
    return not not adapter.getAvailableSizes('image').get('mini')
