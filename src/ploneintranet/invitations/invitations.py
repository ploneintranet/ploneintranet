from zope.component import getUtility
from ploneintranet.invitations.interfaces import ITokenUtility
from Products.Five import BrowserView
from zope.globalrequest import getRequest
from plone import api


class InviteUser(BrowserView):

    def invite_user(self, email_address):
        token_util = getUtility(ITokenUtility)
        token_id = token_util.generate_new_token()
        # TODO - send an email
        return token_id


def accept_invitation(event):
    request = getRequest()
    acl_users = api.portal.get_tool('acl_users')
    username = 'bob@test.com'
    if api.user.get(username=username) is None:
        api.user.create(
            email=username,
            username=username,
        )
    acl_users.updateCredentials(
        request,
        request.response,
        username,
        None
    )
