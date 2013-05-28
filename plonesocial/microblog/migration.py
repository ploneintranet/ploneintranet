from zope.component import queryUtility
from plonesocial.microblog.interfaces import IMicroblogTool
from BTrees import OOBTree

import logging
logger = logging.getLogger('plonesocial.microblog.migration')
from transaction import commit


def setup_uuid_mapping(context):
    """0.5 adds a new index"""
    tool = queryUtility(IMicroblogTool)
    if not hasattr(tool, '_uuid_mapping'):
        logger.info("Adding missing UUID mapping to %s" % repr(tool))
        tool._uuid_mapping = OOBTree.OOBTree()
        commit()
