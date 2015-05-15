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

    def follow(follow_type, actor, other):
        """User <actor> subscribes to <follow_type> <other>"""

    def unfollow(follow_type, actor, other):
        """User <actor> unsubscribes from <follow_type> <other>"""

    def get_following(follow_type, actor):
        """List all <follow_type> that <actor> subscribes to"""

    def get_followers(follow_type, other):
        """List all users that subscribe to <follow_type> <other>"""

    # like API

    def like(like_type, user_id, item_id):
        """User <user_id> likes <like_type> <item_id>"""

    def unlike(like_type, user_id, item_id):
        """User <user_id> unlikes <like_type> <item_id>"""

    def get_likes(like_type, user_id):
        """List all <like_type> liked by <user_id>"""

    def get_likers(like_type, item_id):
        """List all userids liking <like_type> <item_id>"""

    def is_liked(like_type, user_id, item_id):
        """Does <user_id> like <like_type> <item_id>?"""

    # tags API todo


class INetworkTool(INetworkGraph):
    """Provide INetworkContainer as a site utility."""
