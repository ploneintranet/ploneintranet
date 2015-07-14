# -*- coding=utf-8 -*-
from BTrees import OOBTree
from ploneintranet.microblog.interfaces import IMicroblogTool
from ploneintranet.microblog.statusupdate import StatusUpdate
from transaction import commit
from zope.component import queryUtility
import logging

logger = logging.getLogger('ploneintranet.microblog.migration')


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


def uuid_to_microblog_uuid(context):
    '''
    In #506 the status update attribute
    _context_uuid was renamed _microblog_context_uuid

    This upgrade steps makes the existing content uptodate
    '''
    tool = queryUtility(IMicroblogTool)
    i = 0
    for status in tool.values(limit=None):
        if (
            isinstance(status, StatusUpdate)
            and not hasattr(status, '_microblog_context_uuid')
        ):
            i += 1
            uuid = getattr(status, '_context_uuid', None)
            status._microblog_context_uuid = uuid
        if i % 100 == 0:
            commit()
    commit()
