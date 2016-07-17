# coding=utf-8
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.users.browser.passwordpanel import PasswordPanel
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PloneIntranetPasswordPanel(PasswordPanel):
    """Override the account panel template, which uses z3c.form"""

    template = ViewPageTemplateFile('templates/change-password.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        try:
            enable_password_reset = api.portal.get_registry_record(
                'ploneintranet.userprofile.enable_password_reset')
        except InvalidParameterError:
            enable_password_reset = False
        if not enable_password_reset:
            message = _(u'Resetting your own password is not supported.')
            api.portal.show_message(message, self.request, 'error')
            self.request.response.redirect(self.context.absolute_url())
        else:
            super(PloneIntranetPasswordPanel, self).__init__(context, request)

    def validate_password(self, action, data):
        super(PloneIntranetPasswordPanel, self).validate_password(action, data)
        # If there were validation errors, place them into the request so that
        # they can be retrieved in our hand-written form.
        if action.form.widgets.errors:
            errors = {}
            translate = self.context.translate
            for error in action.form.widgets.errors:
                errors[error.widget.name] = translate(error.message)
            self.request.form['errors'] = errors
