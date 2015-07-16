from plone.dexterity import content
from zope.interface import implements, Interface

from ploneintranet.layout.app import AbstractAppContainer
from ploneintranet.layout.interfaces import IAppContainer
from ploneintranet.library.interfaces import ILibraryContentLayer


import logging
log = logging.getLogger(__name__)


class ILibraryApp(IAppContainer):
    """Toplevel Library singleton to contain all library content"""


class ILibrarySection(Interface):
    """Library Sections can contain Folders"""


class ILibraryFolder(Interface):
    """Library Folders can contain Pages and/or sub-Folders"""


class LibraryApp(AbstractAppContainer, content.Container):
    implements(ILibraryApp, IAppContainer)

    app_name = "library"
    app_layers = (ILibraryContentLayer, )


class LibrarySection(content.Container):
    implements(ILibrarySection)


class LibraryFolder(content.Container):
    implements(ILibraryFolder)
