# -*- coding: utf-8 -*-
from plone import api
from plone.memoize.view import memoize
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
    def autosave_enabled(self):
        ''' Look up the registry to check if autosave should be enabled
        for this portal_type
        '''
        autosave_portal_types = api.portal.get_registry_record(
            'ploneintranet.workspace.autosave_portal_types',
            default=[],
        )
        return self.context.portal_type in autosave_portal_types
