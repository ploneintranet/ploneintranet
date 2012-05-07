from zope import schema
from zope.interface import Attribute
from zope.interface import Interface

from plone.app.discussion import PloneAppDiscussionMessageFactory as _


class IStatusContainer(Interface):
    """Manages read/write access to, and storage of,
    IStatusUpdate instances."""

    pass


class IStatusUpdate(Interface):
    """A single 'tweet'."""

    text = schema.Text(title=_(u"label_statusupdate",
                               default=u"Status Update"))
    creator = schema.TextLine(title=_(u"Author name (for display)"))
    userid = schema.TextLine(title=_(u"Userid"))
    creation_date = schema.Date(title=_(u"Creation date"))

    #attachment = Attribute("File attachment.")
    tags = Attribute("Tags/keywords")
