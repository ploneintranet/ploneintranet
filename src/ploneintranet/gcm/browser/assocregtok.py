"""View to associate GCM registration token with a user profile.

"""
from AccessControl import Unauthorized
from Products.Five.browser import BrowserView
from plone import api
from ploneintranet.api import userprofile

from ..interfaces import ITokenAssociation


class GCMUserProfileTokenSave(BrowserView):
    """Associate a GCM registration token with a user profile."""

    def __call__(self):
        if api.user.is_anonymous():
            raise Unauthorized
        response = self.request.respone
        user = api.user.get_current()
        profile = userprofile.get(user.getUserId())
        token_assoc = ITokenAssociation(profile)
        token = token_assoc.save(self.request)
        profile.gcm_reg_id = token
        return response
