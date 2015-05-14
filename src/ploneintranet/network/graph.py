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
    following/unfollowing other users,
    or content objects, status updates, tags.

    All references are string ids.

    Return values are BTrees.OOBTree.OOTreeSet iterables.
    """

    implements(INetworkGraph)
    # API supports multi follow types: (user, content, update, tag)
    supported_follow_types = ('user',)

    def __init__(self, context=None):
        self._following = OOBTree.OOBTree()
        self._followers = OOBTree.OOBTree()
        for follow_type in self.supported_follow_types:
            self._following[follow_type] = OOBTree.OOBTree()
            self._followers[follow_type] = OOBTree.OOBTree()

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
        assert(follow_type in self.supported_follow_types)
        assert(other == str(other))
        """List all users that subscribe to <follow_type> <other>"""
        try:
            return self._followers[follow_type][other]
        except KeyError:
            return ()

    def clear(self, follow_type=None):
        if follow_type:
            assert(follow_type in self.supported_follow_types)
            self._following[follow_type] = OOBTree.OOBTree()
            self._followers[follow_type] = OOBTree.OOBTree()
        else:  # clear all
            for follow_type in self.supported_follow_types:
                self._following[follow_type] = OOBTree.OOBTree()
                self._followers[follow_type] = OOBTree.OOBTree()
