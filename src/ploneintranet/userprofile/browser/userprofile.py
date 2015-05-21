from Products.Five import BrowserView
from Products.CMFPlone.browser.author import AuthorView as BaseAuthorView

from ploneintranet import api as pi_api
from zExceptions import NotFound


class UserProfileView(BrowserView):

    """View for user profile."""

    pass


class AuthorView(BaseAuthorView):
    """Overrides default author view to link to PI profiles"""
    def __call__(self):
        profile = pi_api.userprofile.get(self.username)

        if profile is not None:
            return self.request.response.redirect(
                profile.absolute_url()
            )
        raise NotFound
