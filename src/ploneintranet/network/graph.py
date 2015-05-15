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
    following/unfollowing or liking/unliking or tagging/untagging
    other users, content objects, status updates, tags.

    All references are resolvable, permanently stable, string ids.
    - StatusUpdates: a str() cast of status.id.
    - content: a uuid on the content.
    - users: a stable userid (not a changeable email)
    - tags: merging or renaming tags requires migrating the tag storage

    Return values are BTrees.OOBTree.OOTreeSet iterables.
    """

    implements(INetworkGraph)

    # These statics define the data storage schema "item_type" axes.
    # If you change them you need to carefully migrate the data storage
    # for existing users
    supported_follow_types = ("user", "content", "tag")
    supported_like_types = ("content", "update")

    def __init__(self, context=None):
        """
        Set up storage for personalized data structures.

        FOLLOW: users can follow eachother, or content etc.
        ---------------------------------------------------

        _following["user"][userid] = (userid, userid, ...)
        _followers["user"][userid] = (userid, userid, ...)

        Other follow types can be switched on here but
        are not used anywhere yet.

        LIKE: users can like content or statusupdates
        ---------------------------------------------

        _likes["content"][userid] = (uuid, uuid, ...)
        _liked["content"][uuid] = (userid, userid, ...)

        _likes["update"][userid] = (statusid, statusid, ...)
        _liked["update"][statusid] = (userid, userid, ...)

        TAG: users can apply personal tags on anything.
        -----------------------------------------------

        Not yet implemented, and more complex than following or liking
        since tagging is a 3-way relation (subject, tags, object)

        Endorsements can be implemented as users tagging other users.

        supported_tag_types = ("user", "content", "update")

        Objects tagged by a user:
        _tagged[userid] = {tag: {type: ids}}
        _tagged[userid][tag] = {type: ids}
        _tagged[userid][tag]["user"] = (userid, userid, ...)
        _tagged[userid][tag]["content"] = (uuid, uuid, ...)
        _tagged[userid][tag]["update"] = (statusid, statusid, ...)

        Users that tagged an object:
        _tagger[item_type][id] = {tag: userids}
        _tagger["user"][userid][tag] = (userid, userid, ...)
        _tagger["content"][uuid][tag] = (userid, userid, ...)
        _tagger["update"][statusid][tag] = (userid, userid, ...)

        Find objects by tag:
        _alltagged[tag] = {type: ids}
        _alltagged[tag]["user"] = (userid, userid, ...)
        _alltagged[tag]["content"] = (uuid, uuid, ...)
        _alltagged[tag]["update"] = (statusid, statusid)

        """

        # following
        self._following = OOBTree.OOBTree()
        self._followers = OOBTree.OOBTree()
        for item_type in self.supported_follow_types:
            self._following[item_type] = OOBTree.OOBTree()
            self._followers[item_type] = OOBTree.OOBTree()

        # like
        self._likes = OOBTree.OOBTree()
        self._liked = OOBTree.OOBTree()
        for item_type in self.supported_like_types:
            self._likes[item_type] = OOBTree.OOBTree()
            self._liked[item_type] = OOBTree.OOBTree()

        # tags todo

    # needed in suite/setuphandlers
    clear = __init__

    # following API

    def follow(self, item_type, actor, other):
        """User <actor> subscribes to <item_type> <other>"""
        assert(item_type in self.supported_follow_types)
        assert(actor == str(actor))
        assert(other == str(other))
        # insert user if not exists
        self._following[item_type].insert(actor, OOBTree.OOTreeSet())
        self._followers[item_type].insert(other, OOBTree.OOTreeSet())
        # add follow subscription
        self._following[item_type][actor].insert(other)
        self._followers[item_type][other].insert(actor)

    def unfollow(self, item_type, actor, other):
        """User <actor> unsubscribes from <item_type> <other>"""
        assert(item_type in self.supported_follow_types)
        assert(actor == str(actor))
        assert(other == str(other))
        try:
            self._following[item_type][actor].remove(other)
        except KeyError:
            pass
        try:
            self._followers[item_type][other].remove(actor)
        except KeyError:
            pass

    def get_following(self, item_type, actor):
        """List all <item_type> that <actor> subscribes to"""
        assert(item_type in self.supported_follow_types)
        assert(actor == str(actor))
        try:
            return self._following[item_type][actor]
        except KeyError:
            return ()

    def get_followers(self, item_type, other):
        """List all users that subscribe to <item_type> <other>"""
        assert(item_type in self.supported_follow_types)
        assert(other == str(other))

        try:
            return self._followers[item_type][other]
        except KeyError:
            return ()

    # like API

    def like(self, item_type, user_id, item_id):
        """User <user_id> likes <item_type> <item_id>"""
        assert(item_type in self.supported_like_types)
        assert(user_id == str(user_id))
        assert(item_id == str(item_id))

        self._likes[item_type].insert(user_id, OOBTree.OOTreeSet())
        self._liked[item_type].insert(item_id, OOBTree.OOTreeSet())

        self._likes[item_type][user_id].insert(item_id)
        self._liked[item_type][item_id].insert(user_id)

    def unlike(self, item_type, user_id, item_id):
        """User <user_id> unlikes <item_type> <item_id>"""
        assert(item_type in self.supported_like_types)
        assert(user_id == str(user_id))
        assert(item_id == str(item_id))

        try:
            self._likes[item_type][user_id].remove(item_id)
        except KeyError:
            pass
        try:
            self._liked[item_type][item_id].remove(user_id)
        except KeyError:
            pass

    def get_likes(self, item_type, user_id):
        """List all <item_type> liked by <user_id>"""
        assert(user_id == str(user_id))
        try:
            return self._likes[item_type][user_id]
        except KeyError:
            return []

    def get_likers(self, item_type, item_id):
        """List all userids liking <item_type> <item_id>"""
        assert(item_id == str(item_id))
        try:
            return self._liked[item_type][item_id]
        except KeyError:
            return []

    def is_liked(self, item_type, user_id, item_id):
        """Does <user_id> like <item_type> <item_id>?"""
        assert(user_id == str(user_id))
        assert(item_id == str(item_id))

        try:
            return user_id in self.get_likers(item_type, item_id)
        except KeyError:
            return False

    # tags API todo
