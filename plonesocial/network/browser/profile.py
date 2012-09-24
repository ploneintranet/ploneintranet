from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ProfileView(BrowserView):
    implements(IPublishTraverse)

    index = ViewPageTemplateFile("templates/profile.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.id = None

    def __call__(self):
        return self.render()

    def render(self):
        return self.index()

    def publishTraverse(self, request, name):
        """ used for traversal via publisher, i.e. when using as a url """
        self.id = name
        return self

    @property
    def data(self):
        if self.id:
            return self.mtool.getMemberInfo(self.id)
        elif self.mtool.isAnonymousUser():
            return None
        else:
            return self.mtool.getMemberInfo()

    @property
    def portrait(self):
        """Mugshot."""
        return self.mtool.getPersonalPortrait(self.id)

    @property
    def isAnon(self):
        return self.mtool.isAnonymousUser()

    @property
    def isMine(self):
        """Is this my own profile, or somebody else's?"""
        return self.id == self.mtool.getAuthenticatedMember().getId()

    @property
    def mtool(self):
        return getToolByName(getSite(), 'portal_membership')
