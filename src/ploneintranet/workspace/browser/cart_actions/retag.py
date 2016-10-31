# coding=utf-8
from plone import api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.browser.cart_actions.base import BaseCartView
from ploneintranet.workspace.interfaces import IGroupingStoragable
from ploneintranet.workspace.interfaces import IGroupingStorage
from ploneintranet.workspace.utils import parent_workspace
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import logging

log = logging.getLogger(__name__)


class RetagView(BaseCartView):

    @property
    def workspace(self):
        return parent_workspace(self.context)

    def confirm(self):
        index = ViewPageTemplateFile("templates/retag_confirmation.pt")
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

    def retag(self):
        handled = []
        uids = self.request.form.get('uids', [])
        new_tags = self.request.form.get('subjects')
        if not new_tags:
            return
        parent = parent_workspace(self.context)
        storage = (IGroupingStoragable.providedBy(parent) and
                   IGroupingStorage(parent) or None)
        for uid in uids:
            obj = api.content.get(UID=uid)
            if obj:
                tags_set = set(obj.subject)
                for tag in new_tags.split(','):
                    tags_set.add(safe_unicode(tag))
                obj.subject = tuple(tags_set)
                obj.reindexObject()
                if storage:
                    storage.update_groupings(obj)
                handled.append(u'"%s"' % safe_unicode(obj.Title()))
        if handled:
            titles = ', '.join(sorted(handled))
            msg = _(
                u"batch_retag_success",
                default=u"The following items have been (re)tagged: ${title_elems}",  # noqa
                mapping={"title_elems": titles}
            )
            api.portal.show_message(
                message=msg,
                request=self.request,
                type="success",
            )
        else:
            api.portal.show_message(
                message=_(u"No items could be (re)tagged"),
                request=self.request,
                type="info",
            )

        self.request.response.redirect(self.context.absolute_url())
