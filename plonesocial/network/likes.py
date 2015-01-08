from BTrees import LOBTree
from BTrees import OOBTree
from persistent import Persistent
from Acquisition import Explicit


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

    def add_like(self, userid, object_id, context=None):
        self._user_uuids_mapping[userid] = [object_id]

    def items(self):
        return []
