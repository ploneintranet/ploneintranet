# -*- coding: utf-8 -*-
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import UniqueObject
from ploneintranet.network.graph import NetworkGraph
from ploneintranet.network.interfaces import ILikesTool
from ploneintranet.network.interfaces import INetworkTool
from ploneintranet.network.likes import LikesContainer
from zope.interface import implements


class NetworkTool(UniqueObject, SimpleItem, NetworkGraph):
    """Provide INetworkContainer as a site utility."""

    implements(INetworkTool)

    meta_type = 'ploneintranet.network tool'
    id = 'ploneintranet_network'


class LikesTool(UniqueObject, SimpleItem, LikesContainer):
    """Provide ILikesContainer as a site utility."""

    implements(ILikesTool)

    meta_type = 'ploneintranet.network likes'
    id = 'ploneintranet_likes'
