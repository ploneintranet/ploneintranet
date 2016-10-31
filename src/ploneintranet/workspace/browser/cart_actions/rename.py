# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.browser.cart_actions.base import BaseCartView

import logging

log = logging.getLogger(__name__)


class RenameView(BaseCartView):

    def confirm(self):
        index = ViewPageTemplateFile("templates/rename_confirmation.pt")
        return index(self)

    def items_by_permission(self):
        pm = api.portal.get_tool('portal_membership')
        modifiable = []
        not_modifiable = []
        for item in self.items:
            if pm.checkPermission('Modify portal content', item):
                modifiable.append(item)
            else:
                not_modifiable.append(item)
        return (modifiable, not_modifiable)

    def rename(self):
        handled = []
        uids = self.request.form.get('uids', [])
        for uid in uids:
            obj = api.content.get(UID=uid)
            new_title = self.request.form.get(uid)
            if obj and new_title:
                handled.append(
                    u'"%s" → "%s"' % (
                        safe_unicode(obj.Title()),
                        safe_unicode(new_title)
                    )
                )
                obj.title = new_title
                obj.reindexObject()

        if handled:
            titles = ', '.join(sorted(handled))
            msg = _(
                u"batch_rename_success",
                default=u"The following items have been renamed: ${title_elems}",  # noqa
                mapping={"title_elems": titles}
            )
            api.portal.show_message(
                message=msg,
                request=self.request,
                type="success",
            )
        else:
            api.portal.show_message(
                message=_(u"No items could be renamed"),
                request=self.request,
                type="info",
            )

        self.request.response.redirect(self.context.absolute_url())
