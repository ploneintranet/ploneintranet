import re
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
from plonesocial.activitystream.interfaces import IContentActivity
from plonesocial.activitystream.interfaces import IDiscussionActivity

from plone import api


TAGRE = re.compile('(#(\S+))')
USERRE = re.compile('(@\S+)')


def link_tags(text, url=''):
    tmpl = '<a href="%s/@@stream/tag/\\2" class="tag tag-\\2">\\1</a>'
    return TAGRE.sub(tmpl % url, text)


def link_users(text, url=''):
    user_tmpl = '<a href="{0}/@@profile/{1}" class="user user-{1}">@{2}</a>'
    user_marks = USERRE.findall(text)
    for user_mark in user_marks:
        user_id = user_mark[1:]
        user = api.user.get(username=user_id)
        if user:
            user_fullname = user.getProperty('fullname', '') or user_id
            text = re.sub(
                user_mark,
                user_tmpl.format(
                    url,
                    user_id,
                    user_fullname),
                text
            )
    return text


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
        if self.view.status_id == self.status_id():
            return True

    def statusreply_provider(self):
        if not self.highlight():
            return
        provider = getMultiAdapter(
            (self.status, self.request, self),
            name="plonesocial.microblog.statusreply_provider")
        provider.update()
        return provider()


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
