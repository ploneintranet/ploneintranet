# -*- coding: utf-8 -*-
from Acquisition import aq_chain
from BTrees.OOBTree import OOBTree
from ploneintranet.workspace.workspacefolder import IWorkspaceFolder
from Products.CMFCore.interfaces import ISiteRoot
from plone import api

from zope.annotation import IAnnotations
from zope.component import getUtility


import logging

log = logging.getLogger(__name__)

ANNOTATION_KEY = "ploneintranet.workspace.invitation_storage"

# The type map is used to deduct clear text names for classes and labels
# from portal types
TYPE_MAP = {'Event': 'event',
            'News Item': 'news',
            'Image': 'image',
            'File': 'file',
            'Link': 'link',
            'Folder': 'folder',
            'Document': 'rich',
            'todo': 'task',
            'ploneintranet.workspace.workspacefolder': 'workspace'}


def get_storage(clear=False):
    """helper function to get annotation storage on the portal

    :param clear: If true is passed in, annotations will be cleared
    :returns: portal annotations
    :rtype: IAnnotations

    """
    portal = getUtility(ISiteRoot)
    annotations = IAnnotations(portal)
    if ANNOTATION_KEY not in annotations or clear:
        annotations[ANNOTATION_KEY] = OOBTree()
    return annotations[ANNOTATION_KEY]


def send_email(recipient,
               subject,
               message,
               sender="ploneintranet@netsight.co.uk"):
    """helper function to send an email with the sender preset

    """
    try:
        api.portal.send_email(
            recipient=recipient,
            sender=sender,
            subject=subject,
            body=message)
    except ValueError, e:
        log.error("MailHost error: {0}".format(e))


def parent_workspace(context):
    """ Return containing workspace
        Returns None if not found.
    """
    if IWorkspaceFolder.providedBy(context):
        return context
    for parent in aq_chain(context):
        if IWorkspaceFolder.providedBy(parent):
            return parent


def in_workspace(context):
    return IWorkspaceFolder.providedBy(parent_workspace(context))
