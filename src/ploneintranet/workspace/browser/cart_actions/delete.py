# -*- coding: utf-8 -*-
"""A Cart Action for deleting all items listed in cart."""

from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api

NAME = 'delete'
TITLE = u'Delete'
WEIGHT = 20


class DeleteAction(object):
    """Delete Action implementation that deletes items listed in cart."""

    name = NAME
    title = TITLE
    weight = WEIGHT

    def __init__(self, context):
        self.context = context

    def run(self):
        """Delete all items currently in cart and clear the cart's contents."""
        cart_view = self.context.restrictedTraverse('cart')
        request = self.context.REQUEST
        if len(cart_view.items) == 0:
            api.portal.show_message(
                message="You did not select any documents. Nothing was done.",
                request=request,
                type="warning")
            cart_view._clear()
            return

        handled = list()
        for item in cart_view.items:
            obj = api.content.get(UID=item['UID'])
            if obj is None:
                # An object that is in cart was apparently deleted by someone
                # else and dosn't exist anymore, so there's nothing to do.
                continue
            api.content.delete(obj)
            handled.append(u'"%s"' % safe_unicode(item['Title']))

        api.portal.show_message(
            message=u"The following items have been deleted: %s" % ', '.join(
                sorted(handled)),
            request=request,
            type="success")

        cart_view._clear()


class DeleteView(BrowserView):

    titles = []

    @property
    def items(self):
        items = []
        cart_items = self.request.form.get('shopping-cart')
        if cart_items:
            uids = cart_items.split(',')
            for uid in uids:
                obj = api.content.get(UID=uid)
                if obj:
                    items.append(obj)
        return items

    def confirm(self):
        index = ViewPageTemplateFile("templates/confirm.pt")
        return index(self)

    def delete(self):
        uids = self.request.form.get('uids', [])
        for uid in uids:
            obj = api.content.get(UID=uid)
            self.titles.append(obj.Title())
            api.content.delete(obj)
        self.request.response.redirect(self.context.absolute_url())
