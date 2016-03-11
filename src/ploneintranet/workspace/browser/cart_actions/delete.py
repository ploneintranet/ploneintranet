# -*- coding: utf-8 -*-
"""A Cart Action for deleting all items listed in cart."""
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from ploneintranet.workspace.browser.cart_actions.base import BaseCartView


class DeleteView(BaseCartView):

    def confirm(self):
        index = ViewPageTemplateFile("templates/delete_confirmation.pt")
        return index(self)

    def delete(self):
        handled = []
        uids = self.request.form.get('uids', [])
        for uid in uids:
            obj = api.content.get(UID=uid)
            if obj:
                handled.append(u'"%s"' % safe_unicode(obj.Title()))
                api.content.delete(obj)

        api.portal.show_message(
            message=u"The following items have been deleted: %s" % ', '.join(
                sorted(handled)),
            request=self.request,
            type="success")

        self.request.response.redirect(self.context.absolute_url())
