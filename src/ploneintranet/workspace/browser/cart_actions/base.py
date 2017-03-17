# coding=utf-8
from plone import api
from plone.memoize.view import memoize
from ploneintranet.workspace.interfaces import IGroupingStorage
from ploneintranet.workspace.utils import parent_workspace
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from urllib import urlencode


class BaseCartView(BrowserView):

    titles = []

    checked_permission = 'Modify portal content'

    @property
    @memoize
    def workspace(self):
        return parent_workspace(self.context)

    @property
    @memoize
    def grouping_storage(self):
        return IGroupingStorage(self.workspace, None)

    def update_groupings(self, obj):
        storage = self.grouping_storage
        if not storage:
            return
        storage.update_groupings(obj)

    @property
    def items(self):
        cart_items = self.request.form.get('items', [])
        if not cart_items:
            return []
        brains = api.content.find(UID=cart_items)
        return [b.getObject() for b in brains]

    @memoize
    def items_by_permission(self):
        pm = api.portal.get_tool('portal_membership')
        allowed = []
        unallowed = []
        for item in self.items:
            if pm.checkPermission(self.checked_permission, item):
                allowed.append(item)
            else:
                unallowed.append(item)
        return (allowed, unallowed)

    def confirm(self):
        index = ViewPageTemplateFile("templates/delete_confirmation.pt")
        return index(self)

    def redirect(self):
        ''' Redirect to the context
        '''
        params = {
            'groupname': self.request.get('groupname', ''),
        }
        return self.request.response.redirect(
            '{url}?{params}'.format(
                url=self.context.absolute_url(),
                params=urlencode(params)
            )
        )
