from BTrees.OOBTree import OOBTree
from plone import api
from zope.annotation import IAnnotations
from zope.interface import implements

from .interfaces import ITodoUtility
from .content.content_action import ContentAction

ANNOTATION_KEY = 'ploneintranet.todo.action_storage'


class TodoUtility(object):

    implements(ITodoUtility)

    @staticmethod
    def _get_storage():
        """
        Look up storage for tokens

        :return: action storage
        """
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        if ANNOTATION_KEY not in annotations:
            annotations[ANNOTATION_KEY] = OOBTree()
        return annotations[ANNOTATION_KEY]

    @staticmethod
    def _all_users():
        return [x.getId() for x in api.user.get_users()]

    def _user_in_storage(self, userid):
        storage = self._get_storage()
        return userid in storage

    def query(self, userids=None, verbs=None, content_uids=None, sort_on=None,
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
        if isinstance(userids, basestring):
            userids = [userids]
        if isinstance(verbs, basestring):
            verbs = [verbs]
        if isinstance(content_uids, basestring):
            content_uids = [content_uids]
        return []

    def add_action(self, content_uid, verb, userids=None):
        """
        Add the given action for the given content to the given users, or all
        users

        :param content_uid: The UID of the content
        :type content_uid: str
        :param verb: The action to take
        :type verb: str
        :param userids: The userids to add the action to
        :type userids: list
        """
        if isinstance(userids, basestring):
            userids = [userids]
        storage = self._get_storage()
        if userids is None:
            userids = self._all_users()
        for userid in userids:
            if not self._user_in_storage(userid):
                storage[userid] = []
            user_actions = self.query(
                userids=userid,
                verbs=verb,
                content_uids=content_uid
            )
            if not user_actions:
                user_action = ContentAction(
                    userid,
                    content_uid,
                    verb
                )
                storage[userid].append(user_action)

    def complete_action(self, content_uid, verb, userids=None):
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


