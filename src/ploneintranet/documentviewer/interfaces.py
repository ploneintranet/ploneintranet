from zope.interface import Interface
from zope.interface import Attribute


class IDocumentviewer(Interface):
    ''' The interface for the document_preview view
    '''

    def get_preview(self):
        ''' Get's a preview for this document
        '''


# Async stuff

class IExecutor(Interface):

    def run(func, *args, **kwargs):
        """Runs ``func`` with the provided ``args`` and ``kwargs``.

        It might run immediately or defer to some execution model.
        """


class IAsyncTask(Interface):
    """Marker interface for async class
    """


class IMarshaller(Interface):

    mkey = Attribute("The dotted name of the marshaller class")

    def marshal(*args, **kwargs):
        """Returns a marshalled version of arguments.
        """

    def unmarshal(*marshalled_args, **marshalled_kwargs):
        """Does the exact reverse operation of ``marshal``
        """
