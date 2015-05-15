# -*- coding: utf-8 -*-
from zope.interface import Interface


class INetworkGraph(Interface):
    """Stores a social network graph of users
    following/unfollowing or liking/unliking
    other users, content objects, status updates, tags.

    All references are string ids.

    Return values are BTrees.OOBTree.OOTreeSet iterables.
    """

    # follow API

    def follow(item_type, actor, other):
        """User <actor> subscribes to <item_type> <other>"""

    def unfollow(item_type, actor, other):
        """User <actor> unsubscribes from <item_type> <other>"""

    def get_following(item_type, actor):
        """List all <item_type> that <actor> subscribes to"""

    def get_followers(item_type, other):
        """List all users that subscribe to <item_type> <other>"""

    # like API

    def like(item_type, user_id, item_id):
        """User <user_id> likes <item_type> <item_id>"""

    def unlike(item_type, user_id, item_id):
        """User <user_id> unlikes <item_type> <item_id>"""

    def get_likes(item_type, user_id):
        """List all <item_type> liked by <user_id>"""

    def get_likers(item_type, item_id):
        """List all userids liking <item_type> <item_id>"""

    def is_liked(item_type, user_id, item_id):
        """Does <user_id> like <item_type> <item_id>?"""

    # tags API


class INetworkTool(INetworkGraph):
    """Provide INetworkContainer as a site utility."""
