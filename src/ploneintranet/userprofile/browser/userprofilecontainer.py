# coding=utf-8
from plone import api
from Products.Five import BrowserView


class View(BrowserView):

    def __call__(self):
        ''' This is temporary:
        until we have a view for the profiles folder in proto,
        we redirect the user to the dashboard
        '''
        portal = api.portal.get()
        target = '{}/@@dashboard.html'.format(
            portal.absolute_url(),
        )
        return self.request.response.redirect(target)
