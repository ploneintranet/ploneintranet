# coding=utf-8
from logging import getLogger
from plone import api
from plone.memoize.view import memoize
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.utils import parent_workspace
from Products.Five import BrowserView

logger = getLogger(__name__)


class BaseView(BrowserView):
    ''' A base view that has methods useful for redirects
    '''
    _msg_copy_success = _('copy_success', u'The copy was succesfull')
    _msg_copy_not_allowed = _('copy_not_allowed', u'Copy not allowed')
    _msg_copy_error = _('copy_error', u'Problem during the copy process')

    @property
    @memoize
    def destination(self):
        ''' Get the parent workspace
        '''
        return parent_workspace(self.context)

    def can_copy(self):
        ''' Check if I can copy this context to a parent workspace
        '''
        return True

    def do_copy(self):
        ''' What to do during the copy
        Return a target object (the object copied or its container)
        '''

    def redirect(self, target=None, msg='', msg_type='warning'):
        """
        Has its own method to allow overriding
        """
        if msg:
            api.portal.show_message(msg, self.request, msg_type)
        if not target:
            target = self.context
        if not isinstance(target, basestring):
            context_state = api.content.get_view(
                'plone_context_state',
                target,
                self.request,
            )
            target = context_state.view_url()
        return self.request.response.redirect(target)

    def __call__(self):
        ''' Tries to make the copy

        If it is not possible, warns the user about the problem
        '''
        if not self.can_copy():
            return self.redirect(msg=self._msg_copy_not_allowed)

        try:
            copy = self.do_copy()
        except:
            # If you find an exception here, try to modify the method can_copy
            logger.exception('Problem copying %s', self.context.UID())
            return self.redirect(msg=self._msg_copy_error)

        return self.redirect(
            target=copy,
            msg=self._msg_copy_success,
            msg_type='info',
        )


class AttachmentView(BaseView):
    ''' When called try to make a copy of the content in the parent workspace
    '''
    def do_copy(self):
        ''' do a copy of this object and return the object itself
        '''
        destination = self.destination
        obj = api.content.copy(
            source=self.context,
            target=destination,
            safe_id=True,
        )
        return obj


class MailAttachmentsView(BaseView):
    ''' Copy all the attachments in this email to the parent workspace
    '''
    def do_copy(self):
        ''' do a copy of the contents of this object and return destination
        '''
        destination = self.destination
        for obj in self.context.listFolderContents():
            api.content.copy(
                source=obj,
                target=destination,
                safe_id=True,
            )
        return destination
