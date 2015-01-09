# -*- coding: utf-8 -*-
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import UniqueObject
from plonesocial.network.graph import NetworkGraph
from plonesocial.network.interfaces import ILikesTool
from plonesocial.network.interfaces import INetworkTool
from plonesocial.network.likes import LikesContainer
from zope.interface import implements


class NetworkTool(UniqueObject, SimpleItem, NetworkGraph):
    """Provide INetworkContainer as a site utility."""

    implements(INetworkTool)

    meta_type = 'plonesocial.network tool'
    id = 'plonesocial_network'


class LikesTool(UniqueObject, SimpleItem, LikesContainer):
    """Provide ILikesContainer as a site utility."""

    implements(ILikesTool)

    meta_type = 'plonesocial.network likes'
    id = 'plonesocial_likes'
