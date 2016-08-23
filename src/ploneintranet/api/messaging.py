# -*- coding: utf-8 -*-
import logging
from AccessControl import Unauthorized

from plone import api
from ploneintranet.messaging.messaging import Conversation
from ploneintranet.messaging.interfaces import IMessagingLocator
from zope.component import getUtility

logger = logging.getLogger(__name__)


def send_message(recipient, text, userid=None, when=None):
    """Send text from userid to recipient

    :param recipient: userid of the recipient of the message
    :type recipient: string

    :param text: the message itself
    :type text: string

    :param userid: userid of the sender. Defaults to current user.
    :type userid: string

    :param when: timestamp of the message. Defaults to datetime.now().
    :type when: datetime

    :returns: Sent message
    :rtype: ploneintranet.messaging.interfaces.IMessage
    """
    inboxes = get_inboxes()
    inboxes.send_message(_default(userid), recipient, text, when)


def get_inboxes():
    """
    Get the toplevel messaging accessor with all the inboxes.

    :returns: The toplevel messaging container.
    :rtype: ploneintranet.messaging.interfaces.IInboxes
    """
    locator = getUtility(IMessagingLocator)
    return locator.get_inboxes()


def get_inbox(userid=None):
    """
    Get the inbox for the specified user.

    :param userid: Inbox owner. Defaults to current user.
    :type userid: string

    :returns: Inbox with conversations.
    :rtype: ploneintranet.messaging.interfaces.IInbox
    """
    inboxes = get_inboxes()
    return inboxes[_default(userid)]


def create_inbox(userid=None):
    """
    Create the inbox for the specified user.

    :param userid: Inbox owner. Defaults to current user.
    :type userid: string

    :returns: Inbox with conversations.
    :rtype: ploneintranet.messaging.interfaces.IInbox
    """
    inboxes = get_inboxes()
    _userid = _default(userid)
    if _userid in inboxes.keys():
        raise ValueError("Inbox for %s already exists", userid)
    else:
        return inboxes.add_inbox(_userid)


def get_conversation(other_id, userid=None):
    """
    Get the conversation between two users.

    :param other_id: Userid of somebody else.
    :type other_id: string

    :param userid: Inbox owner. Defaults to current user.
    :type userid: string

    :returns: Conversation with messages.
    :rtyp: ploneintranet.messaging.interfaces.IConversation
    """
    _userid = _default(userid)
    inbox = get_inbox(_userid)
    return inbox[other_id]


def create_conversation(other_id, userid=None):
    """
    Creates an empty conversation if it does not exist in the user's
    inbox. This will NOT create the parallel
    conversation in the other user's inbox. Generally that will
    be auto-created when sending the first message.

    :param other_id: Userid of somebody else.
    :type other_id: string

    :param userid: Inbox owner. Defaults to current user.
    :type userid: string

    :returns: Conversation with messages.
    :rtyp: ploneintranet.messaging.interfaces.IConversation
    """
    _userid = _default(userid)
    inbox = get_inbox(_userid)
    if other_id in inbox.keys():
        raise ValueError("Conversation with %s already exists for %s",
                         other_id, _userid)
    else:
        return inbox.add_conversation(Conversation(other_id))


def get_messages(other_id, userid=None):
    """
    Get the messages between two users.

    :param other_id: Userid of somebody else.
    :type other_id: string

    :param userid: Inbox owner. Defaults to current user.
    :type userid: string

    :returns: iterable of IMessage
    :rtyp: iterable
    """
    return get_conversation(other_id, userid).get_messages()


def _default(userid):
    if not userid:
        userid = api.user.get_current().id
    if not userid:
        raise Unauthorized()
    return userid
