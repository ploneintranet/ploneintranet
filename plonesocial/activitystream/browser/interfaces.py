from zope import schema
from zope.interface import Interface
from zope.interface import Attribute
from zope.contentprovider.interfaces import IContentProvider

from zope.viewlet.interfaces import IViewletManager
from plone.portlets.interfaces import IPortletManager
from plone.app.portlets.interfaces import IColumn
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFPlone import PloneMessageFactory as PMF

from plonesocial.activitystream.interfaces import IActivity

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plonesocial.activitystream')


class IPlonesocialActivitystreamLayer(Interface):
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

    portlet_data = Attribute(
        "Optional slot for IActivitystreamPortlet data access")

    tag = Attribute("Optional tag to filter on")
    userid = Attribute("Optional userid to filter on")


class IPlonesocialActivitystreamViewlets(IViewletManager):
    """A viewlet manager for the activity stream view."""


class IPlonesocialActivitystreamPortlets(IPortletManager, IColumn):
    """A portlet manager for the activity stream view"""


class IActivitystreamPortlet(IPortletDataProvider):
    """A portlet to render the activitystream.
    """

    title = schema.TextLine(title=PMF(u"Title"),
                            description=_(u"A title for this portlet"),
                            required=True,
                            default=u"Activity Stream")

    count = schema.Int(
        title=_(u"Number of updates to display"),
        description=_(u"Maximum number of updates to show"),
        required=True,
        default=5)

    compact = schema.Bool(title=_(u"Compact rendering"),
                          description=_(u"Hide portlet header and footer"),
                          default=True)

    show_microblog = schema.Bool(
        title=_(u"Show microblog"),
        description=_(u"Show microblog status updates"),
        default=True)

    show_content = schema.Bool(
        title=_(u"Show content creation"),
        description=_(u"Show creation of new content"),
        default=True)

    show_discussion = schema.Bool(
        title=_(u"Show discussion"),
        description=_(u"Show discussion replies"),
        default=True)

