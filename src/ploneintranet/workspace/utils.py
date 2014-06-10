from BTrees.OOBTree import OOBTree
from Products.CMFCore.interfaces import ISiteRoot
from plone import api
from zope.annotation import IAnnotations
from zope.component import getUtility


ANNOTATION_KEY = "ploneintranet.workspace.invitation_storage"


def get_storage(clear=False):
    portal = getUtility(ISiteRoot)
    annotations = IAnnotations(portal)
    if ANNOTATION_KEY not in annotations or clear:
        annotations[ANNOTATION_KEY] = OOBTree()
    return annotations[ANNOTATION_KEY]


def send_email(
        recipient,
        subject,
        message,
        sender="ploneintranet@netsight.co.uk"):
    api.portal.send_email(
        recipient=recipient,
        sender=sender,
        subject=subject,
        body=message)
