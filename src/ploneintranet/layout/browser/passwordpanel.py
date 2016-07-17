# coding=utf-8
from plone.app.users.browser.passwordpanel import PasswordPanel
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PloneIntranetPasswordPanel(PasswordPanel):
    """Override the account panel template, which uses z3c.form"""

    template = ViewPageTemplateFile('templates/change-password.pt')

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
