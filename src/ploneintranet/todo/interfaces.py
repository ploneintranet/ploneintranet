# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from zope.interface import Interface, Attribute
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa


# verbs definition
MUST_READ = 'mustread'
TODO = 'todo'


class IContentAction(Interface):
    """
    Interface for ContentAction class
    """
    userid = Attribute(_(u'The userid this action is for'))
    content_uid = Attribute(_(u'The UID of the content that needs actioning'))
    verb = Attribute(_(u'The action to be taken on the content'))
    created = Attribute(_(u'The datetime this ContentAction was created'))
    completed = Attribute(_(u'The datetime this ContentAction was completed'))
    modified = Attribute(_(u'The datetime this ContentAction was triggered'))


class ITodoUtility(Interface):
    """
    Interface for the TodoUtility
    """
    def add_action(content_uid, verb, userids=None, completed=False):
        """
        Add the given action for the given content to the given users, or all
        users. If completed is True then this is an action that has occurred
        (for example "Liking" content) rather than an action that needs to be
        take in the future

        :param content_uid: The UID of the content
        :type content_uid: str
        :param verb: The action to take
        :type verb: str
        :param userids: The userids to add the action to or None for all users
        :type userids: str or list or None
        :param completed: Whether this is a pre-completed action
        :type completed: bool
        """

    def complete_action(content_uid, verb, userids=None):
        """
        Mark the given action for the given content as complete for the given
        users

        :param content_uid: The UID of the content
        :type content_uid: str
        :param verb: The action to complete
        :type verb: str
        :param userids: The userids to complete the action from or None for all
                        users
        :type userids: list or None
        """

    def remove_action(content_uid, verb, userids=None):
        """
        Remove the given action from the users' actions. This is normally for
        admin use, but also for removing pre-completed actions

        :param content_uid: The UID of the content
        :type content_uid: str
        :param verb: The action to complete
        :type verb: str
        :param userids: The userids to complete the action from or None for all
                        users
        :type userids: list or None
        """

    def query(userids=None, verbs=None, content_uids=None, sort_on=None,
              sort_order=None, ignore_completed=True):
        """
        Query the action storage for ContentActions matching the given query.
        Results are AND'd together

        :param userids: UserIDs to lookup
        :type userids: list or str or None
        :param verbs: Action verb to lookup
        :type verbs: list or str or None
        :param content_uids: Content UIDs to lookup
        :type content_uids: list or str or None
        :param sort_on: Field to sort on (created, completed, verb)
        :type sort_on: str
        :param sort_order: Whether to reverse the sort order ('reverse')
        :type sort_order: str or None
        :param ignore_completed: Whether to exclude completed actions from the
               results
        :type ignore_completed: bool
        :return: List of ContentActions
        :rtype: :class: `ContentAction`
        """
