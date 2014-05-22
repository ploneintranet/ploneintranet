from zope.component import getUtility
from ploneintranet.invitations.interfaces import ITokenUtility
from Products.Five import BrowserView
from zope.globalrequest import getRequest
from plone import api


class InviteUser(BrowserView):
    """
    View for sending invitation emails to potential new users of the Plone site
    """
    def invite_user(self, email):
        """
        Get new token, build email and send it to the given email address

        :param email: Email address to send invitation to, and for new user
        :type email: str
        :return:
        """
        token_util = getUtility(ITokenUtility)
        token_id, token_url = token_util.generate_new_token()
        # TODO - send an email
        return token_id, token_url


def accept_invitation(event):
    """
    Event handler for :class:`AcceptToken` event fired by invitation framework

    :param event: The event object
    :type event: :class:`AcceptToken`
    :return:
    """
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
