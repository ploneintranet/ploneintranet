# coding=utf-8
from plone import api
from plone.memoize.view import memoize
from ploneintranet.admintool.browser.interfaces import IGeneratePWResetToken
from Products.Five import BrowserView


class UserCreatedMail(BrowserView):
    ''' An email sent when the user has been created
    '''
    def is_pending(self):
        ''' Check if the user state is pending
        '''
        return api.content.get_state(self.context) == 'pending'

    @property
    @memoize
    def random_string(self):
        ''' Generate a randomstring
        '''
        ppr = api.portal.get_tool('portal_password_reset')
        if not IGeneratePWResetToken.providedBy(self.request):
            return 'exampletoken'
        reset = ppr.requestReset(self.context.username)
        if not reset:
            return ''
        return reset['randomstring']

    @property
    @memoize
    def password_reset_link(self):
        ''' Generate the password reset link
        '''
        ppr = api.portal.get_tool('portal_password_reset')
        return ppr.pwreset_constructURL(self.random_string)
