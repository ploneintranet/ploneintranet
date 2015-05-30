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

    def follow(item_type, item_id, user_id):
        """User <user_id> subscribes to <item_type> <item_id>"""

    def unfollow(item_type, item_id, user_id):
        """User <user_id> unsubscribes from <item_type> <item_id>"""

    def get_following(item_type, user_id):
        """List all <item_type> that <user_id> subscribes to"""

    def get_followers(item_type, item_id):
        """List all users that subscribe to <item_type> <item_id>"""

    def is_followed(item_type, item_id, user_id):
        """Does <user_id> follow <item_type> <item_id>?"""

    # like API

    def like(item_type, item_id, user_id):
        """User <user_id> likes <item_type> <item_id>"""

    def unlike(item_type, item_id, user_id):
        """User <user_id> unlikes <item_type> <item_id>"""

    def get_likes(item_type, user_id):
        """List all <item_type> liked by <user_id>"""

    def get_likers(item_type, item_id):
        """List all userids liking <item_type> <item_id>"""

    def is_liked(item_type, item_id, user_id):
        """Does <user_id> like <item_type> <item_id>?"""

    # tags API

    def tag(item_type, item_id, user_id, *tags):
        """User <user_id> adds tags <*tags> on <item_type> <item_id>"""

    def untag(item_type, item_id, user_id, *tags):
        """User <user_id> removes tags <*tags> from <item_type> <item_id>"""

    def get_tagged(item_type=None, userid=None, tag=None):
        """
        List <item_type> item_ids tagged as <tag> by <user_id>.

        See implementation docstring and test suite for specifications
        of return values when one or more parameters are set to None.
        """

    def get_taggers(item_type, item_id, tag=None):
        """
        List user_ids that tagged <item_type> <item_id> with <tag>.
        If tag==None: returns {tag: (itemids..)} mapping
        """

    def get_tags(item_type, item_id, user_id=None):
        """
        List tags set on <item_type> <item_id> by <user_id>.
        If user_id==None: return {tag: (userids..)} mapping
        """

    def is_tagged(item_type, item_id, user_id, tag):
        """Did <user_id> apply tag <tag> on <item_type> <item_id>?"""


class INetworkTool(INetworkGraph):
    """Provide INetworkContainer as a site utility."""
