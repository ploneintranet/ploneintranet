from zope.interface import Attribute
from zope.interface import Interface


class IStatusContainer(Interface):
    """Manages read/write access to, and storage of,
    IStatusUpdate instances."""

    pass


class IStatusUpdate(Interface):
    """A single 'tweet'."""

    text = Attribute("Text of this activity")
    creator = Attribute("Id of user making this change.")
    date = Attribute("Date (plus time) this activity was made.")
    #attachment = Attribute("File attachment.")
    tags = Attribute("Tags/keywords")
