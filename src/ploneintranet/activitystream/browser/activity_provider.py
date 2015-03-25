from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.component.hooks import getSite

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from plone import api

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from .interfaces import IPloneIntranetActivitystreamLayer
from .interfaces import IActivityProvider
from plone.app.contenttypes.content import Image
from ploneintranet.activitystream.interfaces import IStatusActivity
from ploneintranet.activitystream.interfaces import IStatusActivityReply
from ploneintranet.activitystream.interfaces import IContentActivity
from ploneintranet.activitystream.interfaces import IDiscussionActivity

from ploneintranet.core.integration import PLONEINTRANET
from ploneintranet.core.browser.utils import link_tags
from ploneintranet.core.browser.utils import link_users

try:
    from ploneintranet.attachments.attachments import IAttachmentStoragable
    from ploneintranet.attachments.utils import IAttachmentStorage
except ImportError:
    IAttachmentStoragable = None
try:
    from ploneintranet.docconv.client.interfaces import IDocconv
except ImportError:
    IDocconv = None


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
            url = api.portal.get().absolute_url()
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
        url = api.portal.get().absolute_url()
        text = safe_unicode(self.context.text)
        status = getattr(self, 'status', None)
        tags = getattr(status, 'tags', None)
        mentions = getattr(status, 'mentions', None)
        text += link_users(url, mentions)
        text += link_tags(url, tags)
        return text

    def is_attachment_supported(self):
        return IAttachmentStoragable is not None

    def is_preview_supported(self):
        return IDocconv is not None

    @property
    def attachments(self):
        """
        Get a list of URLs for attachment previews
        (Defined by each activity provider)
        """
        return []

    @property
    def raw_date(self):
        return self.context.raw_date

    @property
    def getId(self):
        pass

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

    @property
    def placeholder(self):
        return u"Leave a comment..."

    def get_toggle_like_view(self):
        portal = api.portal.get()
        toggle_like_base = portal.restrictedTraverse('toggle_like')
        toggle_like_view = toggle_like_base.publishTraverse(
            self.request, self.getId)
        return toggle_like_view


class StatusActivityProvider(AbstractActivityProvider):
    """Render an IStatusActivity"""

    implements(IActivityProvider)
    adapts(IStatusActivity, IPloneIntranetActivitystreamLayer, Interface)

    index = ViewPageTemplateFile("templates/statusactivity_provider.pt")

    def __init__(self, context, request, view):
        self.context = context  # IStatusActivity
        self.status = context.context  # IStatusUpdate
        self.request = request
        self.view = self.__parent__ = view

    @property
    def getId(self):
        return self.status_id()

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
            name="ploneintranet.microblog.statusreply_provider")
        provider.update()
        return provider()

    def reply_providers(self):
        name = (
            "ploneintranet.activitystream.statusactivityinlinereply_provider"
        )
        for reply in self.context.replies():
            provider = getMultiAdapter(
                (reply, self.request, self),
                name=name)
            provider.update()
            yield provider

    @property
    def attachments(self):
        """ Get preview images for status update attachments """
        if not self.is_attachment_supported():
            return []
        if not self.is_preview_supported():
            return []
        if not IAttachmentStoragable.providedBy(self.status):
            return []

        storage = IAttachmentStorage(self.status)
        items = storage.values()
        if not items:
            return []

        attachments = []
        portal_url = api.portal.get().absolute_url()
        base_url = '{portal_url}/@@status-attachments/{status_id}'.format(
            portal_url=portal_url,
            status_id=self.status.getId(),
        )
        for item in items:
            docconv = IDocconv(item)
            if docconv.has_thumbs():
                url = '/'.join((base_url, item.getId(), 'thumb'))
            elif isinstance(item, Image):
                images = api.content.get_view(
                    'images',
                    item.aq_base,
                    self.request,
                )
                url = '/'.join((
                    base_url,
                    item.getId(),
                    images.scale(scale='preview').url.lstrip('/')
                ))
            else:
                url = ''
            if url:
                attachments.append(url)
        return attachments


class StatusActivityReplyProvider(StatusActivityProvider):
    """ Renders a StatusActivity reply in """
    adapts(IStatusActivityReply, IPloneIntranetActivitystreamLayer, Interface)
    index = ViewPageTemplateFile("templates/statusactivityreply_provider.pt")

    def __init__(self, context, request, view):
        """
        Override the __init__ method so that self.status gets defined properly.
        """
        self.context = context  # IStatusUpdate
        self.status = context  # IStatusUpdate
        self.request = request
        self.view = self.__parent__ = view

    def parent_provider(self):
        container = PLONEINTRANET.microblog
        if not container:
            return
        parent = container.get(self.context.thread_id)
        return getMultiAdapter(
            (IStatusActivity(parent), self.request, self.view),
            IActivityProvider)

    @property
    def date(self):
        return self._format_time(self.context.date)

    def status_id(self):
        """
            TEMPORARY HACK - NEEDS TO BE REMOVED
            once the composition of the activity stream gets fixed
        """
        try:
            return self.status.id
        except:
            return None


class StatusActivityInlineReplyProvider(StatusActivityReplyProvider):
    template_name = "templates/statusactivityinlinereply_provider.pt"
    index = ViewPageTemplateFile(template_name)


class ContentActivityProvider(AbstractActivityProvider):
    """Render an IBrainActivity"""

    implements(IActivityProvider)
    adapts(IContentActivity, IPloneIntranetActivitystreamLayer, Interface)

    index = ViewPageTemplateFile("templates/contentactivity_provider.pt")

    @property
    def getId(self):
        return api.content.get_uuid(self.context.context)

    @property
    def attachments(self):
        """ Get preview image for content-related updates"""
        if self.is_preview_supported():
            docconv = IDocconv(self.context.context)
            if docconv.has_thumbs():
                return [self.context.context.absolute_url() +
                        '/docconv_image_thumb.jpg']


class DiscussionActivityProvider(AbstractActivityProvider):
    """Render an IDicussionCommentActivity"""

    implements(IActivityProvider)
    adapts(IDiscussionActivity, IPloneIntranetActivitystreamLayer, Interface)

    index = ViewPageTemplateFile("templates/discussionactivity_provider.pt")

    @property
    def getId(self):
        return api.content.get_uuid(self.context.context)
