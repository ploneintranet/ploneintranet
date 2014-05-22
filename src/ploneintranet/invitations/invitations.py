from Products.CMFCore.interfaces import ISiteRoot
from zope.annotation import IAnnotations
from zope.component import getUtility
from Products.Five import BrowserView
from zope.globalrequest import getRequest
from plone import api
from BTrees.OOBTree import OOBTree
from plone.protect import CheckAuthenticator, PostOnly

from ploneintranet.invitations.interfaces import ITokenUtility


ANNOTATION_KEY = 'ploneintranet.invitations.invitation_storage'


class InviteUser(BrowserView):
    """
    Control panel view for sending invitation emails to potential new users of the Plone site
    """
    def __call__(self):
        email = self.request.form.get('email')
        if email is not None:
            CheckAuthenticator(self.request)
            PostOnly(self.request)
            self.invite_user(email)

        return self.index()

    def invite_user(self, email):
        """
        Get new token, build email and send it to the given email address

        :param email: Email address to send invitation to, and for new user
        :type email: str
        :return: Tuple of token id and token url
        """
        # TODO - check that this email address is not already registered
        portal = api.portal.get()
        token_util = getUtility(ITokenUtility)
        token_id, token_url = token_util.generate_new_token()
        _store_invite(token_id, email)
        message = """You've been invited to join %s

The following is a unique URL that you can use to log in to the site:

%s
""" % (portal.Title(), token_url)
        api.portal.send_email(
            recipient=email,
            subject='Please join my Plone site',
            body=message
        )

        api.portal.show_message(
            'Invitation sent to %s' % email,
            self.request,
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
