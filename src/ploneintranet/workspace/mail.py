# coding=utf-8
from plone.app.contenttypes.content import Folder
from ploneintranet.workspace.interfaces import IMail
from zope.interface import implementer


@implementer(IMail)
class Mail(Folder):
    ''' Convenience subclass for ``ploneintranet.workspace.mail`` portal type
    '''
    disable_add_from_sidebar = True
