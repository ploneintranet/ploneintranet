from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager
from plone.portlets.interfaces import IPortletManager
from plone.app.portlets.interfaces import IColumn


class IPlonesocialActivitystreamLayer(Interface):
    """Marker interface to define ZTK browser layer"""


class IPlonesocialActivitystreamViewlets(IViewletManager):
    """A viewlet manager for the activity stream view."""


class IPlonesocialActivitystreamPortlets(IPortletManager, IColumn):
    """A portlet manager for the activity stream view"""
