# -*- coding: utf-8 -*-
from plone import api
from plone.app.layout.viewlets.content import ContentHistoryView as BaseContentHistoryView  # noqa
from plone.memoize.view import memoize
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from Products.Five.browser import BrowserView


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
        return _('Document locked')

    def unlock(self):
        ''' Unlock this document
        '''
        try:
            self.lock_operations.force_unlock(redirect=False)
        except TypeError:
            # BBB this is for plone.locking < 2.2.0
            self.lock_operations.force_unlock()
        return _('Document unlocked')

    def maybe_toggle(self):
        ''' Check if we should toggle the lock of this object
        '''
        if not self.lock_operations:
            return
        if self.request.form.get('lock'):
            if self.lock_info:
                # Already lock, skip it
                return
            return self.lock()
        if self.request.form.get('unlock'):
            if not self.lock_info:
                return
            return self.unlock()

    def __call__(self):
        ''' Check if we should toggle before rendering the template
        '''
        msg = self.maybe_toggle()
        if msg:
            api.portal.show_message(msg, self.request)
        return super(ToggleLockView, self).__call__()
