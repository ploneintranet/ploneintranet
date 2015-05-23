from zope.interface import implements
from Products.CMFCore.utils import UniqueObject
from OFS.SimpleItem import SimpleItem

from interfaces import IMicroblogTool
from statuscontainer import QueuedStatusContainer


class MicroblogTool(UniqueObject, SimpleItem, QueuedStatusContainer):
    """Provide IStatusContainer as a site utility."""

    implements(IMicroblogTool)

    meta_type = 'ploneintranet.microblog tool'
    id = 'ploneintranet_microblog'
