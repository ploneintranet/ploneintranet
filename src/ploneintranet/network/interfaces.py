# -*- coding: utf-8 -*-
from zope.interface import Interface


class INetworkGraph(Interface):
    """Stores a social network graph of users
    following/unfollowing/blocking eachother.
    """

    def set_follow(follow_type, actor, other):
        """User <actor> subscribes to <follow_type> <other>"""

    def set_unfollow(follow_type, actor, other):
        """User <actor> unsubscribes from <follow_type> <other>"""

    def get_following(follow_type, actor):
        """List all <follow_type> that <actor> subscribes to"""

    def get_followers(follow_type, other):
        """List all users that subscribe to <follow_type> <other>"""


class INetworkTool(INetworkGraph):
    """Provide INetworkContainer as a site utility."""


class ILikesContainer(Interface):
    """Stores likes.
    """


class ILikesTool(ILikesContainer):
    """Provide ILikesContainer as a site utility."""
