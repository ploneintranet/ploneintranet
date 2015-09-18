# -*- coding: utf-8 -*-
from Acquisition import aq_chain
from BTrees.OOBTree import OOBTree
from ploneintranet.workspace.workspacefolder import IWorkspaceFolder
from Products.CMFCore.interfaces import ISiteRoot
from plone import api

from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory

from collective.workspace.interfaces import IWorkspace
from urllib2 import urlparse
import config
import mimetypes
import logging

pl_message = MessageFactory('plonelocales')
log = logging.getLogger(__name__)

ANNOTATION_KEY = "ploneintranet.workspace.invitation_storage"

# The type map is used to deduct clear text names for classes and labels
# from portal types
TYPE_MAP = {'Event': 'event',
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


def existing_users(context):
    """
    Look up the full user details for current workspace members
    """
    members = IWorkspace(context).members
    info = []
    for userid, details in members.items():
        user = api.user.get(userid)
        if user is None:
            continue
        user = user.getUser()
        title = user.getProperty('fullname') or user.getId() or userid
        # XXX tbd, we don't know what a persons description is, yet
        description = ''
        classes = description and 'has-description' or 'has-no-description'
        portal = api.portal.get()
        portrait = '%s/@@avatars/%s' % \
                   (portal.absolute_url(), userid)
        info.append(
            dict(
                id=userid,
                title=title,
                description=description,
                portrait=portrait,
                cls=classes,
                member=True,
                admin='Admins' in details['groups'],
            )
        )

    return info


def set_cookie(request, cookie_name, value):
    """
    Set a cookie to store state.
    This is mainly used by the sidebar to store what grouping was chosen
    """
    full_path = urlparse.urlparse(request.getURL()).path
    if not full_path:  # Test Requests may contain an empty path
        cookie_path = '/TestInstance'
    else:
        cookie_path = '/{0}'.format(full_path.split('/')[1])

    if (cookie_name in request and
        request.get(cookie_name) != value) or \
            cookie_name not in request:
        request.response.setCookie(
            cookie_name, value, path=cookie_path)


def guess_mimetype(file_name):
    content_type = mimetypes.guess_type(file_name)[0]
    # sometimes plone mimetypes registry could be more powerful
    if not content_type:
        mtr = api.portal.get_tool('mimetypes_registry')
        oct = mtr.globFilename(file_name)
        if oct is not None:
            content_type = str(oct)

    return content_type


def map_content_type(mimetype, portal_type=''):
    """
    takes a mimetype and returns a content type string as used in the
    prototype
    """
    content_type = ''
    if portal_type:
        content_type = TYPE_MAP.get(portal_type)

    if not content_type:
        if not mimetype or '/' not in mimetype:
            return content_type

        major, minor = mimetype.split('/')

        if mimetype in config.PDF:
            content_type = 'pdf'
        elif mimetype in config.DOC:
            content_type = 'word'
        elif mimetype in config.PPT:
            content_type = 'powerpoint'
        elif mimetype in config.ZIP:
            content_type = 'zip'
        elif mimetype in config.XLS:
            content_type = 'excel'
        elif mimetype in config.URI:
            content_type = 'link'
        elif mimetype in config.NEWS:
            content_type = 'news'

        elif major == 'text':
            content_type = 'rich'
        elif major == 'audio':
            content_type = 'sound'
        elif major == 'video':
            content_type = 'video'
        elif major == 'image':
            content_type = 'image'

    return content_type


def archives_shown(context, request, section="main"):
    mtool = api.portal.get_tool('portal_membership')
    username = mtool.getAuthenticatedMember().getId()
    cookie_name = '%s-show-extra-%s' % (section, username)
    return 'documents' in request.get(cookie_name, '')


def month_name(self, date):
    """
    Return the full month name in the appropriate language
    """
    translate = self.context.translate
    short_month_name = date.strftime('%b').lower()  # jan
    return translate(pl_message('month_{}'.format(short_month_name)))
