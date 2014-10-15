from zope.interface import Interface


class IDocumentviewer(Interface):
    ''' The interface for the document_preview view
    '''
    def get_preview(self):
        ''' Get's a preview for this document
        '''
