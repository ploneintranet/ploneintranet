from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api


class BaseCartView(BrowserView):

    titles = []

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
