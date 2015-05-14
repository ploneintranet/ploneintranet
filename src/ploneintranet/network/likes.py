# -*- coding: utf-8 -*-
from Acquisition import Explicit
from BTrees import LOBTree
from BTrees import OOBTree
from persistent import Persistent
from ploneintranet.network.interfaces import ILikesContainer
from zope.interface import implementer


@implementer(ILikesContainer)
class LikesContainer(Persistent, Explicit):

    def __init__(self, context=None):
        # maps user id to liked content uids
        self._user_content_mapping = OOBTree.OOBTree()
        # maps content uid to user ids
        self._content_user_mapping = OOBTree.OOBTree()

        # maps user id to liked statusupdaet ids
        self._user_update_mapping = OOBTree.OOBTree()
        # maps status id to user ids
        self._update_user_mapping = LOBTree.LOBTree()

    def like_content(self, user_id, item_id):
        assert(user_id == str(user_id))
        assert(item_id == str(item_id))

        self._user_content_mapping.insert(user_id, OOBTree.OOTreeSet())
        self._content_user_mapping.insert(item_id, OOBTree.OOTreeSet())

        self._user_content_mapping[user_id].insert(item_id)
        self._content_user_mapping[item_id].insert(user_id)

    # suite temporary backcompat
    like = like_content

    def unlike_content(self, user_id, item_id):
        assert(user_id == str(user_id))
        assert(item_id == str(item_id))

        try:
            self._user_content_mapping[user_id].remove(item_id)
        except KeyError:
            pass
        try:
            self._content_user_mapping[item_id].remove(user_id)
        except KeyError:
            pass

    def get_content_likes(self, user_id):
        assert(user_id == str(user_id))
        try:
            return self._user_content_mapping[user_id]
        except KeyError:
            return []

    def get_content_likers(self, item_id):
        assert(item_id == str(item_id))
        try:
            return self._content_user_mapping[item_id]
        except KeyError:
            return []

    def is_content_liked_by_user(self, user_id, item_id):
        try:
            return user_id in self.get_content_likers(item_id)
        except KeyError:
            return False
