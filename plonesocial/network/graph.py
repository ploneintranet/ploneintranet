import logging

from BTrees import LOBTree
from BTrees import OOBTree
from BTrees import LLBTree

from persistent import Persistent
import transaction
from Acquisition import Explicit
from AccessControl import getSecurityManager
from AccessControl import Unauthorized

from zope.interface import implements

from interfaces import INetworkGraph

logger = logging.getLogger('plonesocial.network')


class NetworkGraph(Persistent, Explicit):

    implements(INetworkGraph)
