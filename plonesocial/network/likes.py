from Acquisition import Explicit
from BTrees import LOBTree
from BTrees import OOBTree
from persistent import Persistent
from plonesocial.network.interfaces import ILikesContainer
from zope.interface import implementer


@implementer(ILikesContainer)
class LikesContainer(Persistent, Explicit):

    def __init__(self, context=None):
        # maps user id to liked content uids
        self._user_uuids_mapping = OOBTree.OOBTree()
        # maps content uid to user ids
        self._uuid_userids_mapping = OOBTree.OOBTree()

        # maps user id to liked status ids
        #self._user_statusids_mapping = LOBTree.LOBTree()
        # maps status id to user ids
        #self._statusid_userids_mapping = OOBTree.OOBTree()

    def add(self, user_id, item_id):
        self._user_uuids_mapping[user_id] = [item_id]
        self._uuid_userids_mapping[item_id] = [user_id]

    def like(self, user_id, item_id):
        self.add(user_id, item_id)

    def remove(self, user_id, item_id):
        self._user_uuids_mapping[user_id].remove(item_id)
        self._uuid_userids_mapping[item_id].remove(user_id)

    def unlike(self, user_id, item_id):
        self.remove(user_id, item_id)

    def get(self, user_id):
        try:
            return self._user_uuids_mapping[user_id]
        except KeyError:
            return []

    def get_items_for_user(self, user_id):
        return self.get(user_id)

    def lookup(self, item_id):
        try:
            return self._uuid_userids_mapping[item_id]
        except KeyError:
            return []

    def get_users_for_item(self, item_id):
        return self.lookup(item_id)

    def is_item_liked_by_user(self, user_id, item_id):
        try:
            return user_id in self.lookup(item_id)
        except KeyError:
            return False

    def items(self):
        return []
