from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.component.hooks import getSite

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from AccessControl import getSecurityManager
from Acquisition import aq_inner

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from .interfaces import IPlonesocialActivitystreamLayer
from .interfaces import IActivityProvider
from plonesocial.activitystream.interfaces import IStatusActivity
from plonesocial.activitystream.interfaces import IStatusActivityReply
from plonesocial.activitystream.interfaces import IContentActivity
from plonesocial.activitystream.interfaces import IDiscussionActivity

from plonesocial.core.integration import PLONESOCIAL
from plonesocial.core.browser.utils import link_tags
from plonesocial.core.browser.utils import link_users

try:
    from ploneintranet.attachments.attachments import IAttachmentStoragable
    from ploneintranet.attachments.utils import IAttachmentStorage
    from ploneintranet.docconv.client import IDocconv
except ImportError:
    IAttachmentStoragable = None


class AbstractActivityProvider(object):
    """Helper for rendering IActivity
    """

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = self.__parent__ = view

    def update(self):
        pass

    def render(self):
        return self.index()

    __call__ = render

    def is_anonymous(self):
        portal_membership = getToolByName(getSite(),
                                          'portal_membership',
                                          None)
        return portal_membership.isAnonymousUser()

    def can_review(self):
        """Returns true if current user has the 'Review comments' permission.
        """
        return getSecurityManager(
        ).checkPermission('Review comments',
                          aq_inner(self.context.context))

    @property
    def mtool(self):
        return getToolByName(getSite(), 'portal_membership')

    # IActivityProvider

    @property
    def author_home_url(self):
        if self.userid is None:
            return None
        else:
            portal_state = getMultiAdapter((self.context, self.request),
                                           name=u'plone_portal_state')
            url = portal_state.portal_url()
            return "%s/author/%s" % (url, self.userid)

    @property
    def user_data(self):
        return self.mtool.getMemberInfo(self.userid)

    @property
    def user_portrait(self):
        """Mugshot."""
        return self.mtool.getPersonalPortrait(self.userid)

    @property
    def date(self):
        return self._format_time(self.raw_date)

    def _format_time(self, time):
        # We have to transform Python datetime into Zope DateTime
        # before we can call toLocalizedTime.
        if hasattr(time, 'isoformat'):
            zope_time = DateTime(time.isoformat())
        else:
            # already a Zope DateTime
            zope_time = time
        util = getToolByName(getSite(), 'translation_service')
        if DateTime().Date() == zope_time.Date():
            return util.toLocalizedTime(zope_time,
                                        long_format=True,
                                        time_only=True)
        else:
            # time_only=False still returns time only
            return util.toLocalizedTime(zope_time,
                                        long_format=True)

    # IActivity

    @property
    def url(self):
        site_properties = getToolByName(self.context,
                                        "portal_properties").site_properties
        if self.portal_type in site_properties.typesUseViewActionInListings:
            return self.context.url + '/view'
        else:
            return self.context.url

    @property
    def title(self):
        return self.context.title

    @property
    def userid(self):
        return self.context.userid

    @property
    def Creator(self):
        return self.user_data and self.user_data['fullname'] or self.userid

    @property
    def text(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        url = portal_state.portal_url()
        text = link_users(self.context.text, url)
        return link_tags(text, url)

    @property
    def attachments(self):
        if (IAttachmentStoragable is not None and
                IAttachmentStoragable.providedBy(self.context.context)):
            storage = IAttachmentStorage(self.context.context)
            attachments = storage.values()
            for attachment in attachments:
                docconv = IDocconv(attachment)
                if docconv.has_thumbs():
                    portal_state = getMultiAdapter(
                        (self.context, self.request),
                        name=u'plone_portal_state')
                    url = portal_state.portal_url()
                    yield ('{portal_url}/@@status-attachments/{status_id}/'
                           '{attachment_id}').format(
                               portal_url=url,
                               status_id=self.context.context.getId(),
                               attachment_id=attachment.getId())

    @property
    def raw_date(self):
        return self.context.raw_date

    @property
    def portal_type(self):
        return self.context.portal_type

    @property
    def render_type(self):
        return self.context.render_type

    # extra

    @property
    def getText(self):
        return self.text

    @property
    def getURL(self):
        return self.url

    @property
    def Title(self):
        return self.title


class StatusActivityProvider(AbstractActivityProvider):
    """Render an IStatusActivity"""

    implements(IActivityProvider)
    adapts(IStatusActivity, IPlonesocialActivitystreamLayer, Interface)

    index = ViewPageTemplateFile("templates/statusactivity_provider.pt")

    def __init__(self, context, request, view):
        self.context = context  # IStatusActivity
        self.status = context.context  # IStatusUpdate
        self.request = request
        self.view = self.__parent__ = view

    def status_id(self):
        return self.status.id

    def highlight(self):
        return False
        if self.view.status_id == self.status_id():
            return True

    def statusreply_provider(self):
        # if not self.highlight():
        #     return
        provider = getMultiAdapter(
            (self.status, self.request, self),
            name="plonesocial.microblog.statusreply_provider")
        provider.update()
        return provider()

    def reply_providers(self):
        name = "plonesocial.activitystream.statusactivityinlinereply_provider"
        for reply in self.context.replies():
            provider = getMultiAdapter(
                (reply, self.request, self),
                name=name)
            provider.update()
            yield provider


class StatusActivityReplyProvider(StatusActivityProvider):
    """ Renders a StatusActivity reply in """
    adapts(IStatusActivityReply, IPlonesocialActivitystreamLayer, Interface)
    index = ViewPageTemplateFile("templates/statusactivityreply_provider.pt")

    def parent_provider(self):
        container = PLONESOCIAL.microblog
        if not container:
            return
        parent = container.get(self.context.thread_id)
        return getMultiAdapter(
            (IStatusActivity(parent), self.request, self.view),
            IActivityProvider)


class StatusActivityInlineReplyProvider(StatusActivityReplyProvider):
    template_name = "templates/statusactivityinlinereply_provider.pt"
    index = ViewPageTemplateFile(template_name)

    @property
    def date(self):
        return self._format_time(self.context.date)


class ContentActivityProvider(AbstractActivityProvider):
    """Render an IBrainActivity"""

    implements(IActivityProvider)
    adapts(IContentActivity, IPlonesocialActivitystreamLayer, Interface)

    index = ViewPageTemplateFile("templates/contentactivity_provider.pt")


class DiscussionActivityProvider(AbstractActivityProvider):
    """Render an IDicussionCommentActivity"""

    implements(IActivityProvider)
    adapts(IDiscussionActivity, IPlonesocialActivitystreamLayer, Interface)

    index = ViewPageTemplateFile("templates/discussionactivity_provider.pt")
