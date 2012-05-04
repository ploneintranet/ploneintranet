from DateTime import DateTime
from zope.interface import implements
from zope import schema
from zope.component import queryUtility
from zope.formlib import form
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner, aq_parent
from zope.component import getMultiAdapter
from plone.registry.interfaces import IRegistry
from plone.app.discussion.interfaces import IDiscussionSettings
from AccessControl import getSecurityManager
from zope.app.component.hooks import getSite

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plonesocial.activitystream')


class IActivitystreamPortlet(IPortletDataProvider):
    """A portlet to render the activitystream.
    """

    title = schema.TextLine(title=PMF(u"Title"),
                            description=PMF(u"A title for this portlet"),
                            required=True,
                            default=u"Activity Stream")

    count = schema.Int(
        title=_(u"Number of updates to display"),
        description=_(u"Maximum number of status updates to show"),
        required=True,
        default=5)

    compact = schema.Bool(title=_(u"Compact rendering"),
                          description=_(u"Hide portlet header and footer"),
                          default=True)


class Assignment(base.Assignment):
    implements(IActivitystreamPortlet)

    title = u""  # overrides readonly property method from base class

    def __init__(self,
                 title='Activity Stream',
                 count=5,
                 compact=True):
        self.title = title
        self.count = count
        self.compact = compact


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('activitystream.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self.items = []

    @property
    def available(self):
        return True

    @property
    def compact(self):
        return self.data.compact

    @property
    def portal_url(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.portal_url()

    def update(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        results = []
        brains = catalog.searchResults(sort_on='effective',
                                       sort_order='reverse',
                                       sort_limit=self.data.count,
                                       )[:self.data.count]

        for brain in brains:
            obj = brain.getObject()
            title = obj.Title()
            if obj.portal_type == 'Discussion Item':
                userid = obj.author_username
                text = obj.getText()
                # obj: DiscussionItem
                # parent: Conversation
                # grandparent: content object
                _contentparent = aq_parent(aq_parent(aq_inner(obj)))
                if _contentparent == getSite():
                    # plonesocial.microblog update on siteroot
                    render_type = 'status'
                else:
                    # normal discussion reply
                    render_type = 'discussion'
                    title = _contentparent.Title()
            else:
                userid = obj.getOwnerTuple()[1]
                render_type = 'content'
                text = obj.Description()

            is_status = render_type == 'status'
            is_discussion = render_type == 'discussion'
            is_content = render_type == 'content'

            results.append(dict(
                    getURL=brain.getURL(),
                    Title=title,
                    portal_type=obj.portal_type,
                    render_type=render_type,
                    is_status=is_status,
                    is_discussion=is_discussion,
                    is_content=is_content,
                    userid=userid,
                    Creator=obj.Creator(),
                    has_author_link=self.get_user_home_url(userid) is not None,
                    author_home_url=self.get_user_home_url(userid),
                    portrait_url=self.get_user_portrait(userid),
                    date=self.format_time(obj.creation_date),
                    getText=text,
                    ))

        self.items = results

    def get_user_home_url(self, username=None):
        if username is None:
            return None
        else:
            return "%s/author/%s" % (self.context.portal_url(), username)

    def get_user_portrait(self, username=None):

        if username is None:
            # return the default user image if no username is given
            return 'defaultUser.gif'
        else:
            portal_membership = getToolByName(self.context,
                                              'portal_membership',
                                              None)
            return portal_membership.getPersonalPortrait(username)\
                   .absolute_url()

    def show_commenter_image(self):
        # Check if showing commenter image is enabled in the registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        return settings.show_commenter_image

    def is_anonymous(self):
        portal_membership = getToolByName(self.context,
                                          'portal_membership',
                                          None)
        return portal_membership.isAnonymousUser()

    def format_time(self, time):
        # We have to transform Python datetime into Zope DateTime
        # before we can call toLocalizedTime.
        if hasattr(time, 'isoformat'):
            zope_time = DateTime(time.isoformat())
        else:
            # already a Zope DateTime
            zope_time = time
        util = getToolByName(self.context, 'translation_service')
        if DateTime().Date() == zope_time.Date():
            return util.toLocalizedTime(zope_time,
                                        long_format=True,
                                        time_only=True)
        else:
            # time_only=False still returns time only
            return util.toLocalizedTime(zope_time,
                                        long_format=True)

    def can_review(self):
        """Returns true if current user has the 'Review comments' permission.
        """
        return getSecurityManager().checkPermission('Review comments',
                                                    aq_inner(self.context))


class AddForm(base.AddForm):
    form_fields = form.Fields(IActivitystreamPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IActivitystreamPortlet)
