from zope.interface import implements
from Products.Five import BrowserView
from Products.CMFPlone.browser.author import AuthorView as BaseAuthorView
from zExceptions import NotFound
from AccessControl import Unauthorized
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone import api

from ploneintranet import api as pi_api
from ploneintranet.userprofile.content.userprofile import \
    primaryLocationVocabulary


class UserProfileView(BrowserView):
    implements(IBlocksTransformEnabled)

    """View for user profile."""

    def is_me(self):
        """Does this user profile belong to the current user"""
        return self.context.username == api.user.get_current().getUserName()

    def avatar_url(self):
        """Avatar url for this profile"""
        portal_url = api.portal.get().absolute_url()
        return u'%s/portal_memberdata/portraits/%s' % (
            portal_url,
            self.context.username,
        )

    def primary_location(self):
        """Get context's location using vocabulary."""
        vocabulary = primaryLocationVocabulary(self.context)
        token = self.context.primary_location
        if vocabulary and token:
            return vocabulary.getTermByToken(token).title
        else:
            return ''


class AuthorView(BaseAuthorView):
    """Overrides default author view to link to PI profiles"""

    def __call__(self):
        profile = pi_api.userprofile.get(self.username)

        if profile is not None:
            return self.request.response.redirect(
                profile.absolute_url()
            )
        raise NotFound


class MyProfileView(BaseAuthorView):
    """Helper view to redirect to current user's profile page"""

    def __call__(self):
        profile = pi_api.userprofile.get_current()

        if profile is not None:
            return self.request.response.redirect(
                profile.absolute_url()
            )
        raise Unauthorized
