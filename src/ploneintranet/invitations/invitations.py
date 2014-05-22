from Products.CMFCore.interfaces import ISiteRoot
from zope.annotation import IAnnotations
from zope.component import getUtility
from Products.Five import BrowserView
from zope.globalrequest import getRequest
from plone import api
from BTrees.OOBTree import OOBTree

from ploneintranet.invitations.interfaces import ITokenUtility


ANNOTATION_KEY = 'ploneintranet.invitations.invitation_storage'


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
        _store_invite(token_id, email)
        message = """You've been invited!
%s
""" % token_url
        api.portal.send_email(
            recipient=email,
            subject='Please join my Plone site',
            body=message
        )
        return token_id, token_url


def accept_invitation(event):
    """
    Event handler for :class:`AcceptToken` event fired by invitation framework

    :param event: The event object
    :type event: :class:`AcceptToken`
    :return:
    """
    email = _get_storage().get(event.token_id)
    if email is None:
        return
    request = getRequest()
    acl_users = api.portal.get_tool('acl_users')
    if api.user.get(username=email) is None:
        api.user.create(
            email=email,
            username=email,
        )
    acl_users.updateCredentials(
        request,
        request.response,
        email,
        None
    )


def _get_storage(clear=False):
    portal = getUtility(ISiteRoot)
    annotations = IAnnotations(portal)
    if ANNOTATION_KEY not in annotations or clear:
        annotations[ANNOTATION_KEY] = OOBTree()
    return annotations[ANNOTATION_KEY]


def _store_invite(token_id, email):
    storage = _get_storage()
    storage[token_id] = email
