from zope.component import getUtility
from zope.event import notify
from zope.interface import implements
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import IPublishTraverse
from ploneintranet.invitations.events import TokenAccepted
from ploneintranet.invitations.interfaces import ITokenUtility
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from plone import api


class AcceptToken(BrowserView):
    """
    View that will be called to accept/activate a token

    Usage: /@@accept-token/<token_id>
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
                _("No token id given in sub-path."
                  "Use .../@@accept-token/tokenid")
            )
        util = getUtility(ITokenUtility)
        portal = api.portal.get()
        if util.valid(self.token_id):
            notify(TokenAccepted(self.token_id))
            util._consume_token(self.token_id)
            token = util._fetch_token(self.token_id)
            if token.redirect_path is not None:
                return self.request.response.redirect('%s/%s' % (
                    portal.absolute_url(),
                    token.redirect_path
                ))
        else:
            api.portal.show_message(
                _('Token no longer valid'),
                self.request,
                type='error'
            )
        return self.request.response.redirect(portal.absolute_url())
