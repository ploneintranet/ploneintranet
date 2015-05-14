# -*- coding: utf-8 -*-
from Acquisition import Explicit
from BTrees import OOBTree
from persistent import Persistent
from ploneintranet.network.interfaces import ILikesContainer
from zope.interface import implementer


@implementer(ILikesContainer)
class LikesContainer(Persistent, Explicit):

    supported_like_types = ("content", "update")

    def __init__(self, context=None):
        """
        Set up storage for likes. Structure is similar but separate
        for all supported_like_types:

        - _likes["content"][userid] = (contentid, contentid, ...)
        - _liked["content"][contentid] = (userid, userid, ...)

        - _likes["update"][userid] = (statusid, statusid, ...)
        - _liked["update"][statusid] = (userid, userid, ...)

        """
        self._likes = OOBTree.OOBTree()
        self._liked = OOBTree.OOBTree()
        for like_type in self.supported_like_types:
            self._likes[like_type] = OOBTree.OOBTree()
            self._liked[like_type] = OOBTree.OOBTree()

    def like(self, like_type, user_id, item_id):
        assert(like_type in self.supported_like_types)
        assert(user_id == str(user_id))
        assert(item_id == str(item_id))

        self._likes[like_type].insert(user_id, OOBTree.OOTreeSet())
        self._liked[like_type].insert(item_id, OOBTree.OOTreeSet())

        self._likes[like_type][user_id].insert(item_id)
        self._liked[like_type][item_id].insert(user_id)

    def unlike(self, like_type, user_id, item_id):
        assert(like_type in self.supported_like_types)
        assert(user_id == str(user_id))
        assert(item_id == str(item_id))

        try:
            self._likes[like_type][user_id].remove(item_id)
        except KeyError:
            pass
        try:
            self._liked[like_type][item_id].remove(user_id)
        except KeyError:
            pass

    def get_likes(self, like_type, user_id):
        assert(user_id == str(user_id))
        try:
            return self._likes[like_type][user_id]
        except KeyError:
            return []

    def get_likers(self, like_type, item_id):
        assert(item_id == str(item_id))
        try:
            return self._liked[like_type][item_id]
        except KeyError:
            return []

    def is_liked(self, like_type, user_id, item_id):
        assert(user_id == str(user_id))
        assert(item_id == str(item_id))

        try:
            return user_id in self.get_likers(like_type, item_id)
        except KeyError:
            return False
