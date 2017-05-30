# coding=utf-8
from plone import api
from plone.memoize.view import memoize_contextless
from ploneintranet import api as pi_api
from Products.Five import BrowserView


class View(BrowserView):

    @property
    @memoize_contextless
    def user(self):
        ''' Get the current user profile
        '''
        return pi_api.userprofile.get_current()

    @memoize_contextless
    def get_user(self, userid):
        ''' Given a user id get the user
        '''
        return pi_api.userprofile.get(userid)

    @memoize_contextless
    def get_fullname_for(self, user_or_userid):
        ''' Given a user or a user id return its fullname.
        If not user is found return the user_or_userid argunment
        If the user has no fullname return the userid.
        '''
        if isinstance(user_or_userid, basestring):
            user = self.get_user(user_or_userid)
        else:
            user = user_or_userid
        if not user:
            return user_or_userid
        return user.fullname or user_or_userid

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
