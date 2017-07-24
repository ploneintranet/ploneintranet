# coding=utf-8
from plone.app.content.browser.actions import DeleteConfirmationForm
from plone.memoize.view import memoize
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.interfaces import IModalPanel
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from zope.component import getMultiAdapter
from zope.interface import implementer


@implementer(IModalPanel)
class PIDeleteConfirmationForm(DeleteConfirmationForm):
    ''' We need to override this
    because of some problems with the original delete_confirmation form
    See: https://github.com/plone/plone.app.content/issues/38

    Caveat: we need to reimplement all the actions while overriding,
    because of the button.buttonAndHandler implementation
    '''
    template = ViewPageTemplateFile('templates/delete_confirmation.pt')

    is_modal_panel = True
    panel_size = 'small'
    show_default_cancel_button = False
    title = _('Delete confirmation')

    @property
    @memoize
    def form_action(self):
        ''' Return the z3c.form action
        '''
        return self.action

    @property
    @memoize
    def form_data_pat_inject(self):
        ''' Merge the data inject parts to populate
        the form data-pat-inject attribute
        '''
        return self.request.get('pat-inject')

    @memoize
    def is_ajax(self):
        ''' Check if we have an ajax call
        '''
        requested_with = self.request.environ.get('HTTP_X_REQUESTED_WITH')
        return requested_with == 'XMLHttpRequest'

    def view_url(self):
        ''' Facade to the homonymous plone_context_state method
        '''
        context_state = getMultiAdapter(
            (self.context, self.request),
            name='plone_context_state'
        )
        return context_state.view_url()

    def updateActions(self):
        ''' This method updates the actions to enable some dynamic behaviours

        In particular it understands the request parametes:
         - pat-modal
         - pat-inject

        If pat-modal is truish we add to the action buttons the class
        'close-panel'
        If pat-inject is truish the pat-inject class is added to the form
        and a data attribute data-pat-inject is filled we the value
        read from the request
        '''
        super(PIDeleteConfirmationForm, self).updateActions()

        if self.request.get('pat-modal'):
            self.actions['Delete'].klass = 'icon-ok-circle'
            self.actions['Cancel'].klass = 'close-panel icon-cancel-circle'
            self.actions['Cancel'].type = 'button'
        else:
            self.actions['Delete'].klass = 'icon-ok-circle'
            self.actions['Cancel'].klass = 'icon-cancel-circle close-panel'

    @button.buttonAndHandler(_(u'I am sure, delete now'), name='Delete')
    def handle_delete(self, action):
        base_handler = super(PIDeleteConfirmationForm, self).handle_delete
        return base_handler(self, action)

    @button.buttonAndHandler(
        _(u'label_cancel', default=u'Cancel'), name='Cancel')
    def handle_cancel(self, action):
        return self.request.response.redirect(self.view_url())
