# coding=utf-8
from plone import api
from plone.memoize.view import memoize
from ploneintranet.workspace.utils import parent_workspace
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class BaseCartView(BrowserView):

    titles = []

    checked_permission = 'Modify portal content'

    @property
    @memoize
    def workspace(self):
        return parent_workspace(self.context)

    @property
    def items(self):
        items = []
        cart_items = self.request.form.get('items', [])
        for uid in cart_items:
            obj = api.content.get(UID=uid)
            if obj:
                items.append(obj)
        return items

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
