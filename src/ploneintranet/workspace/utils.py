from Acquisition import aq_chain
from BTrees.OOBTree import OOBTree
from ploneintranet.workspace.workspacefolder import IWorkspaceFolder
from Products.CMFCore.interfaces import ISiteRoot
from plone import api
from zope.annotation import IAnnotations
from zope.component import getUtility


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
    return IWorkspaceFolder.providedBy(parent_workspace(context))


def escape_id_to_class(cid):
    """ We use workspace ids as classes to style them.
        if a workspace has dots in its name, this is not usable as a class
        name. We have to escape that. We might need to do more to them, so this
        became a utility function.
    """
    return cid.replace('.', '-')


def get_workspace_activities(brain, limit=1):
    ''' Return the workspace activities sorted by reverse chronological
    order

    Regarding the time value:
     - the datetime value contains the time in international format
       (machine readable)
     - the title value contains the absolute date and time of the post
    '''
    # BBB: this is a mock!!!!
    return [
        {
            'subject': 'Charlotte Holzer',
            'verb': 'published',
            'object': 'Proposal draft V1.0 # This is a mock!!!',
            'time': {
                'datetime': '2008-02-14',
                'title': '5 October 2015, 18:43',
            }
        }
    ][:limit]


def my_workspaces(context):
    ''' The list of my workspaces
    '''
    pc = api.portal.get_tool('portal_catalog')
    brains = pc(
        portal_type="ploneintranet.workspace.workspacefolder",
        sort_on="modified",
        sort_order="reversed",
    )
    workspaces = [
        {
            'id': brain.getId,
            'title': brain.Title,
            'description': brain.Description,
            'url': brain.getURL(),
            'activities': get_workspace_activities(brain),
            'class': escape_id_to_class(brain.getId),
        } for brain in brains
    ]
    return workspaces
