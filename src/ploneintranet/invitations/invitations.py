from datetime import datetime
from datetime import timedelta

from Products.CMFCore.interfaces import ISiteRoot
from zope.annotation import IAnnotations
from zope.component import getUtility
from Products.Five import BrowserView
from zope.globalrequest import getRequest
from plone import api
from BTrees.OOBTree import OOBTree
from plone.protect import CheckAuthenticator, PostOnly

from ploneintranet.invitations.interfaces import ITokenUtility
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa


ANNOTATION_KEY = 'ploneintranet.invitations.invitation_storage'


class InviteUser(BrowserView):
    """
    Control panel view for sending invitation emails to
    potential new users of the Plone site

    THIS IS EXAMPLE CODE AND NEEDS ATTENTION.
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
        # TODO - Body and subject to become content
        portal = api.portal.get()
        token_util = getUtility(ITokenUtility)
        days = 3
        valid_until, expire_seconds = _ceil_datetime(days=days)
        token_id, token_url = token_util.generate_new_token(
            expire_seconds=expire_seconds)
        _store_invite(token_id, email)
        message = """You've been invited to join %s.

The following is a unique URL tied to your email address (%s).
Clicking the link will create you an account and log in you automatically.

%s

This token will be valid %d days and expire on %s.

Once your account has been created, you can also set up a password
to access the site here:

%s/mail_password_form?userid=%s
""" % (portal.Title(), email, token_url, days, valid_until,
            portal.absolute_url(), email)
        api.portal.send_email(
            recipient=email,
            subject='Your invitation to %s' % portal.Title(),
            body=message
        )

        api.portal.show_message(
            _('Invitation sent to %s') % email,
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
    request = getRequest()
    email = _get_storage().get(event.token_id)
    if email is None:
        api.portal.show_message(_('The token has expired.'), request)
        return
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


def _ceil_datetime(days=3, now=datetime.now()):
    """
    Helper method to ceil the datetime to a quarter of a hour and calculate
    the total_seconds until that moment.

    :param days: the amount of days from now.
    :type days: int
    :param now: The current moment. This is a parameter so we can test.
    :type now: datetime
    :return: (datetime and int)
    """
    valid_until = now + timedelta(days=days)
    valid_until += timedelta(minutes=15)
    valid_until.replace(minute=valid_until.minute % 15).replace(second=0)\
        .replace(microsecond=0)
    expire_seconds = (valid_until - now).total_seconds()
    return valid_until, expire_seconds
