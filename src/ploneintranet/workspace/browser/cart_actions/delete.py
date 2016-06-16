# -*- coding: utf-8 -*-
"""A Cart Action for deleting all items listed in cart."""
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
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

        if handled:
            titles = ', '.join(sorted(handled))
            msg = _(
                u"batch_delete_success",
                default=u"The following items have been deleted: ${title_elems}",  # noqa
                mapping={"title_elems": titles}
            )
            api.portal.show_message(
                message=msg,
                request=self.request,
                type="success",
            )
        else:
            api.portal.show_message(
                message=_(u"No items could be deleted"),
                request=self.request,
                type="info",
            )

        self.request.response.redirect(self.context.absolute_url())

    def items_by_permission(self):
        pm = api.portal.get_tool('portal_membership')
        deletable = []
        not_deletable = []
        for item in self.items:
            if pm.checkPermission('Delete objects', item):
                deletable.append(item)
            else:
                not_deletable.append(item)
        return (deletable, not_deletable)
