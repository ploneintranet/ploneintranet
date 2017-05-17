# -*- coding: utf-8 -*-
from plone import api
from plone.memoize.view import memoize
from ploneintranet import api as pi_api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from Products.Five import BrowserView


class View(BrowserView):
    ''' The helper view the renders the saving badge or a simple save button
    '''
    _edit_permission = 'Modify portal content'

    @property
    @memoize
    def can_edit(self):
        ''' Check if the user can edit
        '''
        return api.user.has_permission(
            self._edit_permission,
            obj=self.context
        )

    @property
    @memoize
    def lock_info(self):
        ''' return info if the object is locked, otherwise return None
        '''
        try:
            view = api.content.get_view(
                'plone_lock_info',
                self.context,
                self.request,
            )
        except api.exc.InvalidParameterError:
            return
        info = view.lock_info()
        if not info:
            return
        user = pi_api.userprofile.get_current()
        if info.get('creator') == user.id:
            return
        info['lock_panel_link_title'] = _(
            'lock_panel_link_title',
            default=(
                u'This item is locked by ${fullname}. '
                u'Click to see options.'
            ),
            mapping={'fullname': info['fullname']},
        )
        return info

    @property
    @memoize
    def autosave_enabled(self):
        ''' Look up the registry to check if autosave should be enabled
        for this portal_type
        '''
        autosave_portal_types = api.portal.get_registry_record(
            'ploneintranet.workspace.autosave_portal_types',
            default=[],
        )
        return self.context.portal_type in autosave_portal_types
