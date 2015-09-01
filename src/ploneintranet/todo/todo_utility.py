from operator import itemgetter
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
        """
        Get all userids for the site

        :return: The userids of all site users
        :rtype: list
        """
        return [x.getId() for x in api.user.get_users()]

    def _user_in_storage(self, userid):
        """
        Does the given userid exist in the annotation storage?

        :param userid: The userid to check
        :type userid: str
        :return: Whether the userid is in storage or not
        :rtype: bool
        """
        storage = self._get_storage()
        return userid in storage

    def _create_user_storage(self, userid):
        """
        Initialise user's ContentAction storage

        :param userid: The userid to initialise
        :type userid: str
        """
        if not self._user_in_storage(userid):
            storage = self._get_storage()
            storage[userid] = []

    def _get_action_for_user(self, content_uid, verb, users_actions):
        for idx, x in enumerate(users_actions):
            if x.verb == verb and x.content_uid == content_uid:
                return users_actions.pop(idx), users_actions

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
        if userids is None:
            userids = self._all_users()
        reverse = True if sort_order == 'reverse' else False
        storage = self._get_storage()
        actions = []

        # Get a list of all actions for the given userids
        for userid in userids:
            self._create_user_storage(userid)
            actions.extend(storage[userid])

        # Filter on verbs
        if verbs is not None:
            actions = [x for x in actions if x.verb in verbs]

        # Filter content_uids
        if content_uids is not None:
            actions = [x for x in actions if x.content_uid in content_uids]

        # Filter completed
        if ignore_completed:
            actions = [x for x in actions if x.completed is None]

        # Sort results
        if sort_on is not None:
            return sorted(actions, key=itemgetter(sort_on), reverse=reverse)
        return actions

    def add_action(self, content_uid, verb, userids=None, completed=False):
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
        if isinstance(userids, basestring):
            userids = [userids]
        storage = self._get_storage()
        if userids is None:
            userids = self._all_users()
        for userid in userids:
            self._create_user_storage(userid)
            user_actions = [
                x for x in storage[userid]
                if x.verb == verb and x.content_uid == content_uid
            ]
            if not user_actions:
                user_action = ContentAction(
                    userid,
                    content_uid,
                    verb
                )
                if completed:
                    user_action.mark_complete()
                storage[userid].append(user_action)
            # TODO: If the action exists we perhaps should update 'modified'

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
        :type userids: list or str or None
        """
        if isinstance(userids, basestring):
            userids = [userids]
        if userids is None:
            userids = self._all_users()
        storage = self._get_storage()

        for userid in userids:
            if userid in storage and storage[userid]:
                users_actions = storage[userid]
                action, users_actions = self._get_action_for_user(
                    content_uid,
                    verb,
                    users_actions
                )
                action.mark_complete()
                users_actions.append(action)
                storage[userid] = users_actions

    def remove_action(self, content_uid, verb, userids=None):
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
        if isinstance(userids, basestring):
            userids = [userids]
        if userids is None:
            userids = self._all_users()
        storage = self._get_storage()

        for userid in userids:
            users_actions = storage[userid]
            _, users_actions = self._get_action_for_user(
                content_uid,
                verb,
                users_actions
            )
            storage[userid] = users_actions
