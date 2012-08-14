from zope.interface import Interface

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plonesocial.network')


class INetworkGraph(Interface):
    """Stores a social network graph of users
    following/unfollowing/blocking eachother.
    """


class INetworkTool(INetworkGraph):
    """Provide INetworkContainer as a site utility."""
