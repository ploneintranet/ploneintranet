from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api


class BaseCartView(BrowserView):

    titles = []

    @property
    def items(self):
        items = []
        cart_items = self.request.form.get('shopping-cart')
        if cart_items:
            uids = cart_items.split(',')
            for uid in uids:
                obj = api.content.get(UID=uid)
                if obj and obj.aq_parent == self.context:
                    items.append(obj)
        return items

    def confirm(self):
        index = ViewPageTemplateFile("templates/delete_confirmation.pt")
        return index(self)
