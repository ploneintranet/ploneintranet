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


def setup_threadids(context):
    """0.6 adds a new statuscontainerindex and statusupdate attribute"""
    tool = queryUtility(IMicroblogTool)
    if not hasattr(tool, '_threadid_mapping'):
        logger.info("Adding missing threadid mapping to %s" % repr(tool))
        tool._threadid_mapping = OOBTree.OOBTree()
        commit()
    i = 0
    for status in tool.values(limit=None):
        i += 1
        if getattr(status, 'thread_id', False) is False:
            status.thread_id = None
        if i % 100 == 0:
            commit()
    commit()
