# coding=utf-8
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.actions import DeleteConfirmationForm
from z3c.form import button
from zope.component import getMultiAdapter


class PIDeleteConfirmationForm(DeleteConfirmationForm):
    ''' We need to override this
    because of some problems with the original delete_confirmation form
    See: https://github.com/plone/plone.app.content/issues/38

    Caveat: we need to reimplement all the actions while overriding,
    because of the button.buttonAndHandler implementation
    '''
    template = ViewPageTemplateFile('templates/delete_confirmation.pt')

    def view_url(self):
        ''' Facade to the homonymous plone_context_state method
        '''
        context_state = getMultiAdapter(
            (self.context, self.request),
            name='plone_context_state'
        )
        return context_state.view_url()

    @button.buttonAndHandler(_(u'Delete'), name='Delete')
    def handle_delete(self, action):
        base_handler = super(PIDeleteConfirmationForm, self).handle_delete
        return base_handler(self, action)

    @button.buttonAndHandler(
        _(u'label_cancel', default=u'Cancel'), name='Cancel')
    def handle_cancel(self, action):
        return self.request.response.redirect(self.view_url())
