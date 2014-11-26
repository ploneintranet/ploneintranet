# -*- coding: utf-8 -*-
from .graph import NetworkGraph
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import UniqueObject
from interfaces import INetworkTool
from zope.interface import implements


class NetworkTool(UniqueObject, SimpleItem, NetworkGraph):
    """Provide INetworkContainer as a site utility."""

    implements(INetworkTool)

    meta_type = 'plonesocial.network tool'
    id = 'plonesocial_network'
