from DateTime import DateTime
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

    def date(self, date):
        ''' The date of our context object
        '''
        # We have to transform Python datetime into Zope DateTime
        # before we can call toLocalizedTime.
        time = date
        if hasattr(time, 'isoformat'):
            time = DateTime(self.context.raw_date.isoformat())

        if DateTime().Date() == time.Date():
            time_only = True
        else:
            # time_only=False still returns time only
            time_only = None

        toLocalizedTime = api.portal.get_tool('translation_service').toLocalizedTime
        return toLocalizedTime(
            time,
            long_format=True,
            time_only=time_only
        )
