from zope import schema
from zope.interface import Attribute
from zope.interface import Interface

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plonesocial.microblog')


class IStatusUpdate(Interface):
    """A single 'tweet'."""

    id = schema.Int(title=_(u"A longint unique status id"))
    text = schema.Text(title=_(u"label_statusupdate",
                               default=u"Status Update"))
    creator = schema.TextLine(title=_(u"Author name (for display)"))
    userid = schema.TextLine(title=_(u"Userid"))
    creation_date = schema.Date(title=_(u"Creation date"))
    tags = Attribute("Tags/keywords")


class IStatusContainer(Interface):
    """Manages read/write access to, and storage of,
    IStatusUpdate instances.

    IStatusContainer provides a subset of a ZODB IBTree interface.

    Some IBTree methods are blocked because they would destroy
    consistency of the internal data structures.

    IStatusContainer manages a more complex data structure than
    just a BTree: it also provides for user and tag indexes.
    These are covered in additional methods.
    """

    def add(status):
        """Add a IStatusUpdate.

        Actual storage may be queued for later insertion by
        the implementation.

        Returns 1 on completion of synchronous insertion.
        Returns 0 when the actual insertion is queued for later processing.
        """

    def store(status):
        """Add a IStatusUpdate, forcing immediate disk commit.

        Don't use this unless you know what you're doing,
        it will limit capacity to a handful of messages per second.
        """

    def clear(self):
        """Empty the status storage and all indexes."""

    ## primary accessors

    def get(key):
        """Fetch an IStatusUpdate by IStatusUpdate.id key."""

    def items(min=None, max=None):
        """BTree compatible accessor.
        min and max are longint IStatusUpdate.id keys.
        """

    def keys(min=None, max=None):
        """BTree compatible accessor.
        min and max are longint IStatusUpdate.id keys.
        """

    def values(min=None, max=None):
        """BTree compatible accessor.
        min and max are longint IStatusUpdate.id keys.
        """

    def iteritems(min=None, max=None):
        """BTree compatible accessor.
        min and max are longint IStatusUpdate.id keys.
        """

    def iterkeys(min=None, max=None):
        """BTree compatible accessor.
        min and max are longint IStatusUpdate.id keys.
        """

    def itervalues(min=None, max=None):
        """BTree compatible accessor.
        min and max are longint IStatusUpdate.id keys.
        """

    ## user accessors

    def user_items(users, min=None, max=None):
        """Filter (key, IStatusUpdate) items by iterable of userids.
        min and max are longint IStatusUpdate.id keys.
        """

    def user_keys(users, min=None, max=None):
        """Filter IStatusUpdate keys by iterable of userids.
        min and max are longint IStatusUpdate.id keys.
        """

    def user_values(users, min=None, max=None):
        """Filter IStatusUpdate values by iterable of userids.
        min and max are longint IStatusUpdate.id keys.
        """
