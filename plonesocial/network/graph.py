import logging

from BTrees import OOBTree
from persistent import Persistent
from Acquisition import Explicit

from zope.interface import implements

from interfaces import INetworkGraph

logger = logging.getLogger('plonesocial.network')


class NetworkGraph(Persistent, Explicit):
    """Stores a social network graph of users
    following/unfollowing/blocking eachother.

    Users are referenced as string userids.

    Return values are BTrees.OOBTree.OOTreeSet iterables.
    """

    implements(INetworkGraph)

    def __init__(self, context=None):
        self._following = OOBTree.OOBTree()
        self._followers = OOBTree.OOBTree()

    def set_follow(self, actor, other):
        """User <actor> subscribes to user <other>"""
        assert(actor == str(actor))
        assert(other == str(other))
        # insert user if not exists
        self._following.insert(actor, OOBTree.OOTreeSet())
        self._followers.insert(other, OOBTree.OOTreeSet())
        # add follow subscription
        self._following[actor].insert(other)
        self._followers[other].insert(actor)

    def set_unfollow(self, actor, other):
        """User <actor> unsubscribes from user <other>"""
        assert(actor == str(actor))
        assert(other == str(other))
        try:
            self._following[actor].remove(other)
        except KeyError:
            pass
        try:
            self._followers[other].remove(actor)
        except KeyError:
            pass

    def get_following(self, actor):
        """List all users that <actor> subscribes to"""
        assert(actor == str(actor))
        try:
            return self._following[actor]
        except KeyError:
            return ()

    def get_followers(self, actor):
        assert(actor == str(actor))
        """List all users that subscribe to <actor>"""
        try:
            return self._followers[actor]
        except KeyError:
            return ()

    def clear(self):
        self._following = OOBTree.OOBTree()
        self._followers = OOBTree.OOBTree()
