# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.browser.cart_actions.base import BaseCartView
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from urllib import urlencode

import logging


log = logging.getLogger(__name__)


class RenameView(BaseCartView):

    def confirm(self):
        index = ViewPageTemplateFile("templates/rename_confirmation.pt")
        return index(self)

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

        params = {
            'groupname': self.request.get('groupname', ''),
        }
        self.request.response.redirect(
            '{0}?{1}'.format(
                self.context.absolute_url(), urlencode(params)))
