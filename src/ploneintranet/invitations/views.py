from zope.component import getUtility
from zope.interface import implements
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import IPublishTraverse
from ploneintranet.invitations.interfaces import ITokenUtility
from plone import api


class Invitation(BrowserView):
    """
    View that will be called to consume a token

    Usage: /@@invitations/<token_id>
    """
    implements(IPublishTraverse)

    token_id = None

    def publishTraverse(self, request, name):
        self.token_id = name
        self.request = request
        return self

    def __call__(self):
        if self.token_id is None:
            raise KeyError(
                "No token id given in sub-path."
                "Use .../@@invitations/tokenid")
        util = getUtility(ITokenUtility)
        if util._consume_token(self.token_id):
            api.portal.show_message('Invitation accepted',
                                    self.request, type='info')
        else:
            api.portal.show_message('Invalid code no longer valid',
                                    self.request, type='error')
        portal = api.portal.get()
        self.request.response.redirect(portal.absolute_url())
