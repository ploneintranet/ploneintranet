# -*- coding: utf-8 -*-
from Acquisition import Explicit
from BTrees import OOBTree
from interfaces import INetworkGraph
from persistent import Persistent
from zope.interface import implements
import logging

logger = logging.getLogger('ploneintranet.network')


class NetworkGraph(Persistent, Explicit):
    """Stores a social network graph of users
    following/unfollowing or liking/unliking
    other users, content objects, status updates, tags.

    All references are string ids.

    Return values are BTrees.OOBTree.OOTreeSet iterables.
    """

    implements(INetworkGraph)
    # follow API supports multi follow types: (user, content, update, tag)
    supported_follow_types = ('user',)  # adding here is enough
    # like API supports multi like types
    supported_like_types = ("content", "update")

    def __init__(self, context=None):
        """
        Set up storage for personalized data structures.

        FOLLOW: users can follow eachother, or content etc.

        _following["user"][userid] = (userid, userid, ...)
        _followers["user"][userid] = (userid, userid, ...)

        LIKE: users can like content or statusupdates

        _likes["content"][userid] = (contentid, contentid, ...)
        _liked["content"][contentid] = (userid, userid, ...)

        _likes["update"][userid] = (statusid, statusid, ...)
        _liked["update"][statusid] = (userid, userid, ...)

        TAG: users can apply personal tags on anything.
        Not yet implemented, and more complex than following or liking
        since tagging is a 3-way relation (subject, tags, object)
        """

        # following
        self._following = OOBTree.OOBTree()
        self._followers = OOBTree.OOBTree()
        for follow_type in self.supported_follow_types:
            self._following[follow_type] = OOBTree.OOBTree()
            self._followers[follow_type] = OOBTree.OOBTree()

        # like
        self._likes = OOBTree.OOBTree()
        self._liked = OOBTree.OOBTree()
        for like_type in self.supported_like_types:
            self._likes[like_type] = OOBTree.OOBTree()
            self._liked[like_type] = OOBTree.OOBTree()

        # tags todo

    # needed in suite/setuphandlers
    clear = __init__

    # following API

    def set_follow(self, follow_type, actor, other):
        """User <actor> subscribes to <follow_type> <other>"""
        assert(follow_type in self.supported_follow_types)
        assert(actor == str(actor))
        assert(other == str(other))
        # insert user if not exists
        self._following[follow_type].insert(actor, OOBTree.OOTreeSet())
        self._followers[follow_type].insert(other, OOBTree.OOTreeSet())
        # add follow subscription
        self._following[follow_type][actor].insert(other)
        self._followers[follow_type][other].insert(actor)

    def set_unfollow(self, follow_type, actor, other):
        """User <actor> unsubscribes from <follow_type> <other>"""
        assert(follow_type in self.supported_follow_types)
        assert(actor == str(actor))
        assert(other == str(other))
        try:
            self._following[follow_type][actor].remove(other)
        except KeyError:
            pass
        try:
            self._followers[follow_type][other].remove(actor)
        except KeyError:
            pass

    def get_following(self, follow_type, actor):
        """List all <follow_type> that <actor> subscribes to"""
        assert(follow_type in self.supported_follow_types)
        assert(actor == str(actor))
        try:
            return self._following[follow_type][actor]
        except KeyError:
            return ()

    def get_followers(self, follow_type, other):
        """List all users that subscribe to <follow_type> <other>"""
        assert(follow_type in self.supported_follow_types)
        assert(other == str(other))

        try:
            return self._followers[follow_type][other]
        except KeyError:
            return ()

    # like API

    def like(self, like_type, user_id, item_id):
        """User <user_id> likes <like_type> <item_id>"""
        assert(like_type in self.supported_like_types)
        assert(user_id == str(user_id))
        assert(item_id == str(item_id))

        self._likes[like_type].insert(user_id, OOBTree.OOTreeSet())
        self._liked[like_type].insert(item_id, OOBTree.OOTreeSet())

        self._likes[like_type][user_id].insert(item_id)
        self._liked[like_type][item_id].insert(user_id)

    def unlike(self, like_type, user_id, item_id):
        """User <user_id> unlikes <like_type> <item_id>"""
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
        """List all <like_type> liked by <user_id>"""
        assert(user_id == str(user_id))
        try:
            return self._likes[like_type][user_id]
        except KeyError:
            return []

    def get_likers(self, like_type, item_id):
        """List all userids liking <like_type> <item_id>"""
        assert(item_id == str(item_id))
        try:
            return self._liked[like_type][item_id]
        except KeyError:
            return []

    def is_liked(self, like_type, user_id, item_id):
        """Does <user_id> like <like_type> <item_id>?"""
        assert(user_id == str(user_id))
        assert(item_id == str(item_id))

        try:
            return user_id in self.get_likers(like_type, item_id)
        except KeyError:
            return False

    # tags API todo
