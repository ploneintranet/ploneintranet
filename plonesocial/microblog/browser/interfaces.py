from zope.interface import Interface
from zope.interface import Attribute
from zope.contentprovider.interfaces import IContentProvider

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plonesocial.microblog')


class IPlonesocialMicroblogLayer(Interface):
    """Marker interface to define ZTK browser layer"""


class IStatusProvider(IContentProvider):
    """Microblog input form as a content provider"""

    portlet_data = Attribute(
        "Optional slot for portlet data access")
