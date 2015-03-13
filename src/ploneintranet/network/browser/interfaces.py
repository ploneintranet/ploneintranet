# -*- coding: utf-8 -*-
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import Attribute
from zope.interface import Interface


class IPloneIntranetNetworkLayer(Interface):
    '''Marker interface to define ZTK browser layer'''


class IAuthorProvider(IContentProvider):
    '''Marker interface to define author helpers'''

    userid = Attribute('The guy in the author view')
    viewer_id = Attribute('The guy looking at the author')
    data = Attribute('User data on userid')
    portrait = Attribute('Portrait of userid')
    is_anonymous = Attribute('Is the viewer anon?')
    is_mine = Attribute('Is this the author view of the viewer_id?')
    is_following = Attribute('Is viewer_id following user_id?')
    show_subunsub = Attribute('Whether to show sub/unsub buttons?')
