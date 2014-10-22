from zope.interface import Interface


class IDocumentviewer(Interface):
    ''' The interface for the document_preview view
    '''

    def get_preview_url(self):
        ''' Get's a preview url for this document
        '''

    def get_preview_image(self):
        ''' Get's a preview image for this document
        '''


class IExecutor(Interface):

    def run(func, *args, **kwargs):
        """Runs ``func`` with the provided ``args`` and ``kwargs``.

        It might run immediately or defer to some execution model.
        """
