# coding=utf-8
from plone import api
from plone.locking.browser.locking import LockingInformation
from ploneintranet import api as pi_api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PILockingInformation(LockingInformation):
    ''' Locking informations for Plone Intranet
    '''
    panel_template = ViewPageTemplateFile('templates/locking_panel.pt')

    def chat_link(self):
        ''' If the user is a ploneintranet user profile,
        return a link to open a chat with him.
        '''
        info = self.lock_info()
        if not info:
            return {}
        user = pi_api.userprofile.get(info.get('creator'))
        if not user:
            return {}
        portal = api.portal.get()
        try:
            app = portal.apps.messages
        except AttributeError:
            return {}

        app_tile = api.content.get_view('app-tile', app, self.request)
        if app_tile.disabled:
            return {}
        return {
            'url': '{app_url}/{userid}/#end-of-conversation'.format(
                app_url=app_tile.url,
                userid=user.id,
            ),
            'label': _(
                'lock_panel_chat_link_label',
                default=(
                    u'Chat with ${fullname}.'
                ),
                mapping={'fullname': user.fullname or user.id},
            )
        }

    def render_panel(self):
        ''' Render the locking panel
        '''
        return self.panel_template()
