# coding=utf-8
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.browser.actions import PIDeleteConfirmationForm
from ploneintranet.workspace.utils import parent_workspace
from z3c.form import button


class TodoDeleteConfirmationForm(PIDeleteConfirmationForm):
    ''' Override the Delete confirmation view to redirect to the todo app
    if the task is in the userprofile context.

    Note: we need to override both the actions
    '''
    @button.buttonAndHandler(_(u'I am sure, delete now'), name='Delete')
    def handle_delete(self, action):
        base_handler = super(TodoDeleteConfirmationForm, self).handle_delete
        base_handler(self, action)
        if not self.request.form.get('app') and parent_workspace(self.context):
            return
        url = self.context.apps['todo'].app_url()
        return self.request.response.redirect(url)

    @button.buttonAndHandler(
        _(u'label_cancel', default=u'Cancel'), name='Cancel')
    def handle_cancel(self, action):
        return self.request.response.redirect(self.view_url())
