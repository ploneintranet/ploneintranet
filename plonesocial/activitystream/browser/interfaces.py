from zope.interface import Interface
from zope.interface import Attribute
from zope.contentprovider.interfaces import IContentProvider

from zope.viewlet.interfaces import IViewletManager
from plone.portlets.interfaces import IPortletManager
from plone.app.portlets.interfaces import IColumn

from plonesocial.activitystream.interfaces import IActivity


class IPlonesocialActivitystreamLayer(Interface):
    """Marker interface to define ZTK browser layer"""


class IPlonesocialActivitystreamViewlets(IViewletManager):
    """A viewlet manager for the activity stream view."""


class IPlonesocialActivitystreamPortlets(IPortletManager, IColumn):
    """A portlet manager for the activity stream view"""


class IActivityContentProvider(IContentProvider, IActivity):
    """Helper to render IActivity"""

    has_author_link = Attribute("author home url is not None")
    author_home_url = Attribute("author home url")
    portrait_url = Attribute("author portrait url")
    date = Attribute("formatted datetime")

    # + all the IActivity accessors
