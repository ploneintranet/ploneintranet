import logging

from BTrees import LOBTree
from BTrees import OOBTree
from BTrees import LLBTree

from persistent import Persistent
import transaction
from Acquisition import Explicit
from AccessControl import getSecurityManager
from AccessControl import Unauthorized

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
        self._followees = OOBTree.OOBTree()
        self._followers = OOBTree.OOBTree()

    def set_follow(self, actor, other):
        """User <actor> subscribes to user <other>"""
        assert(actor == str(actor))
        assert(other == str(other))
        # insert user if not exists
        self._followees.insert(actor, OOBTree.OOTreeSet())
        self._followers.insert(other, OOBTree.OOTreeSet())
        # add follow subscription
        self._followees[actor].insert(other)
        self._followers[other].insert(actor)

    def set_unfollow(self, actor, other):
        """User <actor> unsubscribes from user <other>"""
        assert(actor == str(actor))
        assert(other == str(other))
        self._followees[actor].remove(other)
        self._followers[other].remove(actor)

    def get_followees(self, actor):
        """List all users that <actor> subscribes to"""
        assert(actor == str(actor))
        return self._followees[actor]

    def get_followers(self, actor):
        assert(actor == str(actor))
        """List all users that subscribe to <actor>"""
        return self._followers[actor]
