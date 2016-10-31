# coding=utf-8
from plone import api
from plone.api.exc import InvalidParameterError
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from zope.publisher.browser import BrowserView


class VerifyPasswordResetAllowed(BrowserView):
    """
        Check if users are allowed to reset their password.
        Redirect to given URL otherwise.
        This mimicks the way the old rejectAnonymous script from
        Archetypes used to work.
    """

    def __call__(self, redirect_url=''):
        try:
            enable_password_reset = api.portal.get_registry_record(
                'ploneintranet.userprofile.enable_password_reset')
        except InvalidParameterError:
            enable_password_reset = False
        if not enable_password_reset:
            message = _(u'Resetting your own password is not supported.')
            api.portal.show_message(message, self.request, 'error')
            if not redirect_url:
                redirect_url = self.context.absolute_url()
            self.request.response.redirect(redirect_url)
        return True
