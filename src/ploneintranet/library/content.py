from plone.app.textfield import RichText
from plone.dexterity import content
from zope.interface import implements, Interface

from . import _

import logging
log = logging.getLogger(__name__)


class ILibraryApp(Interface):
    """Toplevel Library singleton to contain all library content"""


class ILibrarySection(Interface):
    """Library Sections can contain Folders"""


class ILibraryFolder(Interface):
    """Library Folders can contain Pages and/or sub-Folders"""


class ILibraryPage(Interface):
    """A library leaf page, which may contain non-folderish helper objects"""

    text = RichText(
        title=_(u"Text"),
        description=_(u"Body text"),
        required=True,
    )


class LibraryApp(content.Container):
    implements(ILibraryApp)


class LibrarySection(content.Container):
    implements(ILibrarySection)


class LibraryFolder(content.Container):
    implements(ILibraryFolder)


class LibraryPage(content.Container):
    implements(ILibraryPage)
