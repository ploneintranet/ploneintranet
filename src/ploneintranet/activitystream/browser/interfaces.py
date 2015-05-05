from zope.interface import Interface
from zope.interface import Attribute
from zope.contentprovider.interfaces import IContentProvider

from ploneintranet.activitystream.interfaces import IActivity

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('ploneintranet.activitystream')


class IPloneIntranetActivitystreamLayer(Interface):
    """Marker interface to define ZTK browser layer"""


class IActivityProvider(IContentProvider, IActivity):
    """Helper to render IActivity"""

    author_home_url = Attribute("author home url")
    user_data = Attribute("author memberinfo dict")
    user_portrait = Attribute("author portrait url")
    date = Attribute("formatted datetime")

    # + all the IActivity accessors


class IStreamProvider(IContentProvider):
    """Helper to render activity streams"""

    tag = Attribute("Optional tag to filter on")
    userid = Attribute("Optional userid to filter on")


class IStatusConversationProvider(IContentProvider):
    """Helper to render status conversations"""
