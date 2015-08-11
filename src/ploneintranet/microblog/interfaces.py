from zope import schema
from zope.interface import Attribute
from zope.interface import Interface

from plone.uuid.interfaces import IUUIDAware

from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa


class IStatusUpdate(Interface):
    """A single 'tweet'."""

    id = schema.Int(title=_(u"A longint unique status id"))
    text = schema.Text(title=_(u"add_statusupdate_button",
                               default=u"What are you doing?"))
    creator = schema.TextLine(title=_(u"Author name (for display)"))
    userid = schema.TextLine(title=_(u"Userid"))
    creation_date = schema.Date(title=_(u"Creation date"))
    tags = Attribute("Tags/keywords")

    # the UUID of the IMicroblogContext
    context_UUID = Attribute("UUID of IMicroblogContext (e.g. a workspace)")
    # actual object context
    context_object = Attribute("UUID of context object (e.g. a Page)")
    thread_id = Attribute("status.id from parent")

    def replies():
        """ Return a list of replies (IStatusUpdate)"""


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

    def clear():
        """Empty the status storage and all indexes."""

    # primary accessors

    def get(key):
        """Fetch an IStatusUpdate by IStatusUpdate.id key."""

    def items(min=None, max=None, limit=100, tag=None):
        """BTree compatible accessor.
        min and max are longint IStatusUpdate.id keys.
        limit returns [:limit] most recent items
        tag 'foo' filters status text on hashtag '#foo'
        """

    def keys(min=None, max=None, limit=100, tag=None):
        """BTree compatible accessor.
        min and max are longint IStatusUpdate.id keys.
        limit returns [:limit] most recent items
        tag 'foo' filters status text on hashtag '#foo'
        """

    def values(min=None, max=None, limit=100, tag=None):
        """BTree compatible accessor.
        min and max are longint IStatusUpdate.id keys.
        limit returns [:limit] most recent items
        tag 'foo' filters status text on hashtag '#foo'
        """

    iteritems = items
    iterkeys = keys
    itervalues = values

    # user_* accessors

    def user_items(users, min=None, max=None, limit=100, tag=None):
        """Filter (key, IStatusUpdate) items by iterable of userids.
        min and max are longint IStatusUpdate.id keys.
        limit returns [:limit] most recent items
        tag 'foo' filters status text on hashtag '#foo'
        """

    def user_keys(users, min=None, max=None, limit=100, tag=None):
        """Filter IStatusUpdate keys by iterable of userids.
        min and max are longint IStatusUpdate.id keys.
        limit returns [:limit] most recent items
        tag 'foo' filters status text on hashtag '#foo'
        """

    def user_values(users, min=None, max=None, limit=100, tag=None):
        """Filter IStatusUpdate values by iterable of userids.
        min and max are longint IStatusUpdate.id keys.
        limit returns [:limit] most recent items
        tag 'foo' filters status text on hashtag '#foo'
        """

    # context_* accessors

    def context_items(context, min=None, max=None, limit=100, tag=None):
        """Filter (key, IStatusUpdate) items by IMicroblogContext object.
        min and max are longint IStatusUpdate.id keys.
        limit returns [:limit] most recent items
        context <object> filters on StatusUpdates keyed to that context's UUID.
        """

    def context_keys(context, min=None, max=None, limit=100, tag=None):
        """Filter IStatusUpdate keys by IMicroblogContext object.
        min and max are longint IStatusUpdate.id keys.
        limit returns [:limit] most recent items
        tag 'foo' filters status text on hashtag '#foo'
        """

    def context_values(context, min=None, max=None, limit=100, tag=None):
        """Filter IStatusUpdate values by IMicroblogContext object.
        min and max are longint IStatusUpdate.id keys.
        limit returns [:limit] most recent items
        tag 'foo' filters status text on hashtag '#foo'

        """

    # mention_* accessors

    def mention_items(mentions, min=None, max=None, limit=100, tag=None):
        """Filter (key, IStatusUpdate) items by mentions.
        min and max are longint IStatusUpdate.id keys.
        limit returns [:limit] most recent items
        tag 'foo' filters status text on hashtag '#foo'
        """

    def mention_keys(mentions, min=None, max=None, limit=100, tag=None):
        """Filter IStatusUpdate keys by mentions.
        min and max are longint IStatusUpdate.id keys.
        limit returns [:limit] most recent items
        tag 'foo' filters status text on hashtag '#foo'
        """

    def mention_values(mentions, min=None, max=None, limit=100, tag=None):
        """Filter IStatusUpdate values by mentions.
        min and max are longint IStatusUpdate.id keys.
        limit returns [:limit] most recent items
        tag 'foo' filters status text on hashtag '#foo'
        """


class IMicroblogTool(IStatusContainer):
    """Provide IStatusContainer as a site utility."""


class IMicroblogContext(IUUIDAware):
    """Marker interface for non-SiteRoot objects with a local microblog.
    Such objects should be adaptable to provide a UUID.
    """


class IURLPreview(Interface):
    """Tool to generate url preview image"""

    def generate_previews(url):
        """Return web preview image urls, in most cases it's the OG link."""
