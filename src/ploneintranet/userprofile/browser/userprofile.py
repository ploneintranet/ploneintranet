from Products.Five import BrowserView
from Products.CMFPlone.browser.author import AuthorView as BaseAuthorView

from plone import api
from ploneintranet import api as pi_api
from zExceptions import NotFound


class UserProfileView(BrowserView):

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


class AuthorView(BaseAuthorView):
    """Overrides default author view to link to PI profiles"""
    def __call__(self):
        profile = pi_api.userprofile.get(self.username)

        if profile is not None:
            return self.request.response.redirect(
                profile.absolute_url()
            )
        raise NotFound
