"""View to associate GCM registration token with a user profile.

"""
import json
import logging

from AccessControl import Unauthorized
from Products.Five.browser import BrowserView
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from ploneintranet.api import userprofile
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

from ..interfaces import ITokenAssociation


logger = logging.getLogger(__name__)


class ProfileAssociation(BrowserView):
    """View that associates a GCM registration token with a user profile.

    This is currently demo-quality - a real API should check a CRSF token.
    """

    def __call__(self, REQUEST=None):
        """Saves the token against the current user profile.

        If not user is present, return a HTTP 403 Unauthorized response.

        The `REQUEST` paramter is required for compliance with plone.protect.
        """
        request = REQUEST if REQUEST is not None else self.request
        alsoProvides(request, IDisableCSRFProtection)
        response = request.response
        if api.user.is_anonymous():
            raise Unauthorized
        user = api.user.get_current()
        profile = userprofile.get(user.getUserId())
        token_assoc = getMultiAdapter((profile, request),
                                      ITokenAssociation)
        token = token_assoc.save(self.request)
        profile.gcm_reg_id = token
        response.setStatus(200)
        response.write(json.dumps(dict(token=token, status='OK')))
        return response
