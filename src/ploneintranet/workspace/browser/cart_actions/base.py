# coding=utf-8
from plone import api
from plone.memoize.view import memoize
from ploneintranet.workspace.utils import parent_workspace
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class BaseCartView(BrowserView):

    titles = []

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

    def confirm(self):
        index = ViewPageTemplateFile("templates/delete_confirmation.pt")
        return index(self)
