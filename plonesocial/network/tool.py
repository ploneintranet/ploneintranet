from zope.interface import implements
from Products.CMFCore.utils import UniqueObject
from OFS.SimpleItem import SimpleItem

from interfaces import INetworkTool
from graph import NetworkGraph


class NetworkTool(UniqueObject, SimpleItem, NetworkGraph):
    """Provide INetworkContainer as a site utility."""

    implements(INetworkTool)

    meta_type = 'plonesocial.network tool'
    id = 'plonesocial_network'
