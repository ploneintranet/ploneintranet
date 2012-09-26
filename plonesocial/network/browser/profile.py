from zope.interface import implements
from zope.component import getMultiAdapter, ComponentLookupError
from zope.publisher.interfaces import IPublishTraverse

from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.memoize import view


class ProfileView(BrowserView):
    implements(IPublishTraverse)

    index = ViewPageTemplateFile("templates/profile.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._userid = None

    def __call__(self):
        return self.render()

    def render(self):
        return self.index()

    def publishTraverse(self, request, name):
        """ used for traversal via publisher, i.e. when using as a url """
        self._userid = name
        return self

    @property
    def userid(self):
        if self._userid:
            return self._userid
        elif self.is_anonymous:
            return None
        else:
            return self.mtool.getAuthenticatedMember().getId()

    @property
    @view.memoize
    def data(self):
        return self.mtool.getMemberInfo(self.userid)

    @property
    def portrait(self):
        """Mugshot."""
        return self.mtool.getPersonalPortrait(self.userid)

    @property
    def is_anonymous(self):
        return self.mtool.isAnonymousUser()

    @property
    def is_mine(self):
        """Is this my own profile, or somebody else's?"""
        return self.id == self.mtool.getAuthenticatedMember().getId()

    @property
    def mtool(self):
        return getToolByName(getSite(), 'portal_membership')

    def stream_provider(self):
        try:
            # plonesocial.activitystream integration is optional
            provider = getMultiAdapter(
                (self.context, self.request, self),
                name="plonesocial.activitystream.stream_provider")
            provider.userid = self.userid
            return provider()
        except ComponentLookupError:
            # no plonesocial.activitystream available
            return ''
