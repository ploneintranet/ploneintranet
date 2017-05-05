# coding=utf-8
from plone.memoize.view import memoize_contextless
from ploneintranet.layout.interfaces import IAppView
from Products.Five import BrowserView
from zope.interface import implementer


@implementer(IAppView)
class View(BrowserView):
    ''' The view for this app
    '''
    app_name = 'administrator-tool'

    @property
    @memoize_contextless
    def navigation_tabs(self):
        ''' Navigation tabs
        '''
        tabs = [
            'Requests worklist',
            'Workspace management',
            'User management',
            'Group management',
        ]
        tabs = []  # BBB
        return tabs
