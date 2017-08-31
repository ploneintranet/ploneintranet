# coding=utf-8
from plone import api
from plone.indexer.decorator import indexer
from ploneintranet.userprofile.content.userprofile import IUserProfile
from ploneintranet.userprofile.content.workgroup import IWorkGroup
from Products.membrane.interfaces import IMembraneUserObject
from zope.interface import Interface


@indexer(IUserProfile)
def Title(ob, **kw):
    """Add support for the Title index/metadata from Products.membrane"""
    user = IMembraneUserObject(ob, None)
    if user:
        return user.get_full_name()
    return ""


@indexer(IUserProfile)
def sortable_title(ob, **kw):
    """Sorting users happens by last name"""
    user = IMembraneUserObject(ob, None)
    if user:
        names = [
            ob.last_name,
            ob.first_name,
        ]
        return u' '.join([name for name in names if name])
    return ""


@indexer(IUserProfile)
def login_time(obj):
    ''' Return the userprofile login time
    '''
    user = api.user.get(obj.username)
    return user and user.getProperty('login_time', None)


@indexer(Interface)
def login_time_default(obj):
    ''' Dummy login_time adapter for objects that do not support that indexer
    '''


@indexer(IWorkGroup)
def workspace_members(self):
    return set(self.members)
