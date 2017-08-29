# coding=utf-8
from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.view import memoize_contextless


class Viewlet(ViewletBase):
    ''' Check if the on screen help toggle button should be displayed
    in the portal header
    '''
    def update(self):
        ''' We do not need the attributes set by the default update method
        '''
        return

    @memoize_contextless
    def available(self):
        ''' This will be available if the site has bubbles enabled
        '''
        portal = api.portal.get()
        view = api.content.get_view(
            'on-screen-help',
            portal,
            self.request,
        )
        return bool(view.bubbles)
