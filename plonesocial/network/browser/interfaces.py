from zope.interface import Interface
from zope.interface import Attribute
from zope.contentprovider.interfaces import IContentProvider


class IPlonesocialNetworkLayer(Interface):
    """Marker interface to define ZTK browser layer"""


class IProfileProvider(IContentProvider):
    """Marker interface to define profile helpers"""

    userid = Attribute("The guy in the profile")
    viewer_id = Attribute("The guy looking at the profile")
    data = Attribute("User data on userid")
    portrait = Attribute("Portrait of userid")
    is_anonymous = Attribute("Is the viewer anon?")
    is_mine = Attribute("Is this the profile of the viewer_id?")
    is_following = Attribute("Is viewer_id following user_id?")
    show_subunsub = Attribute("Whether to show sub/unsub buttons?")
