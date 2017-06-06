# -*- coding: utf-8 -*-
from plone import api
from plone.memoize.view import memoize
from ploneintranet import api as pi_api
from ploneintranet.layout.interfaces import IDiazoNoTemplate
from Products.Five.browser import BrowserView
from zope.interface import implementer


@implementer(IDiazoNoTemplate)
class ToggleLockView(BrowserView):
    ''' Toggle the lock
    '''
    @property
    @memoize
    def lock_info(self):
        ''' Info about this document locking state
        '''
        try:
            return api.content.get_view(
                'plone_lock_info',
                self.context,
                self.request,
            ).lock_info()
        except api.exc.InvalidParameterError:
            pass

    @property
    @memoize
    def lock_operations(self):
        ''' The view that handles the operations for us
        '''
        try:
            return api.content.get_view(
                'plone_lock_operations',
                self.context,
                self.request,
            )
        except api.exc.InvalidParameterError:
            pass

    def lock(self):
        ''' Lock this document
        '''
        try:
            self.lock_operations.create_lock(redirect=False)
        except TypeError:
            # BBB this is for plone.locking < 2.2.0
            self.lock_operations.create_lock()

    @property
    @memoize
    def user(self):
        ''' The currently authenticated ploneintranet user profile (if any)
        '''
        return pi_api.userprofile.get_current()

    def can_lock(self):
        ''' Check if we can lock this document
        '''
        # If we cannot edit the document, we should not lock it
        return api.user.has_permission(
            'Modify portal content',
            obj=self.context,
        )

    def can_unlock(self):
        ''' Check if we can unlock this document
        '''
        lock_info = self.lock_info
        if not lock_info:
            return False
        user = self.user
        if not user:
            return False
        return lock_info.get('creator') == user.username

    def unlock(self):
        ''' Unlock this document
        '''
        try:
            self.lock_operations.force_unlock(redirect=False)
        except TypeError:
            # BBB this is for plone.locking < 2.2.0
            self.lock_operations.force_unlock()

    def maybe_toggle(self):
        ''' Check if we should toggle the lock of this object
        '''
        if not self.lock_operations:
            # Document does not support locking
            return
        if self.request.form.get('lock') and self.can_lock():
            if self.lock_info:
                return
            return self.lock()
        if self.request.form.get('unlock') and self.can_unlock():
            return self.unlock()

    def __call__(self):
        ''' Check if we should toggle before rendering the template
        '''
        msg = self.maybe_toggle()
        if msg:
            api.portal.show_message(msg, self.request)
        return super(ToggleLockView, self).__call__()
