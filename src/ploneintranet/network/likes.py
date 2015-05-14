# -*- coding: utf-8 -*-
from Acquisition import Explicit
from BTrees import LOBTree
from BTrees import LLBTree
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

    # unified interface
    supported_like_types = ("content", "update")

    def like(self, like_type, user_id, item_id):
        assert like_type in self.supported_like_types
        if like_type == "content":
            self.like_content(user_id, item_id)
        elif like_type == "update":
            self.like_update(user_id, item_id)

    def unlike(self, like_type, user_id, item_id):
        assert like_type in self.supported_like_types
        if like_type == "content":
            self.unlike_content(user_id, item_id)
        elif like_type == "update":
            self.unlike_update(user_id, item_id)

    def get_likes(self, like_type, user_id):
        assert like_type in self.supported_like_types
        if like_type == "content":
            return self.get_content_likes(user_id)
        elif like_type == "update":
            return self.get_update_likes(user_id)

    def get_likers(self, like_type, item_id):
        assert like_type in self.supported_like_types
        if like_type == "content":
            return self.get_content_likers(item_id)
        elif like_type == "update":
            return self.get_update_likers(item_id)

    def is_liked(self, like_type, user_id, item_id):
        assert like_type in self.supported_like_types
        if like_type == "content":
            return self.is_content_liked(user_id, item_id)
        elif like_type == "update":
            return self.is_update_liked(user_id, item_id)

    # content variants

    def like_content(self, user_id, item_id):
        assert(user_id == str(user_id))
        assert(item_id == str(item_id))

        self._user_content_mapping.insert(user_id, OOBTree.OOTreeSet())
        self._content_user_mapping.insert(item_id, OOBTree.OOTreeSet())

        self._user_content_mapping[user_id].insert(item_id)
        self._content_user_mapping[item_id].insert(user_id)

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

    def is_content_liked(self, user_id, item_id):
        assert(user_id == str(user_id))
        assert(item_id == str(item_id))

        try:
            return user_id in self.get_content_likers(item_id)
        except KeyError:
            return False

    # statusupdate variants

    def like_update(self, user_id, item_id):
        assert(user_id == str(user_id))
        assert(long(item_id))
        item_id = long(item_id)  # support string input

        self._user_update_mapping.insert(user_id, LLBTree.LLTreeSet())
        self._update_user_mapping.insert(item_id, OOBTree.OOTreeSet())

        self._user_update_mapping[user_id].insert(item_id)
        self._update_user_mapping[item_id].insert(user_id)

    def unlike_update(self, user_id, item_id):
        assert(user_id == str(user_id))
        assert(long(item_id))
        item_id = long(item_id)  # support string input

        try:
            self._user_update_mapping[user_id].remove(item_id)
        except KeyError:
            pass
        try:
            self._update_user_mapping[item_id].remove(user_id)
        except KeyError:
            pass

    def get_update_likes(self, user_id):
        assert(user_id == str(user_id))

        try:
            return self._user_update_mapping[user_id]
        except KeyError:
            return []

    def get_update_likers(self, item_id):
        assert(long(item_id))
        item_id = long(item_id)  # support string input

        try:
            return self._update_user_mapping[item_id]
        except KeyError:
            return []

    def is_update_liked(self, user_id, item_id):
        assert(user_id == str(user_id))
        assert(long(item_id))
        item_id = long(item_id)  # support string input

        try:
            return user_id in self.get_update_likers(item_id)
        except KeyError:
            return False
