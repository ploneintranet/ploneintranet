from plone import api
from plone.app.contenttypes.interfaces import IDocument
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.tiles import Tile


class MyDocumentsTile(Tile):

    def my_documents(self):
        """
        Return the 10 most recently modified documents which I have the
        permission to view.
        """
        catalog = api.portal.get_tool('portal_catalog')

        recently_modified_items = catalog.searchResults(
            object_provides=[
                IDocument.__identifier__,
                IFile.__identifier__,
                IImage.__identifier__,
            ],
            sort_on='modified',
            sort_limit=10,
            sort_order='descending',
        )
        return recently_modified_items
