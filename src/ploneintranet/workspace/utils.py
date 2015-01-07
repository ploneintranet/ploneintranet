from Acquisition import aq_chain
from BTrees.OOBTree import OOBTree
from ploneintranet.workspace.workspacefolder import IWorkspaceFolder
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone import api
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.component import hooks


ANNOTATION_KEY = "ploneintranet.workspace.invitation_storage"


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
    api.portal.send_email(
        recipient=recipient,
        sender=sender,
        subject=subject,
        body=message)


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
    return IWorkspaceState.providedBy(parent_workspace(context))
