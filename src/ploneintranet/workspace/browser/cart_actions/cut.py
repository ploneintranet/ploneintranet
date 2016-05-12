# -*- coding: utf-8 -*-
from OFS.CopySupport import _cb_encode
from OFS.CopySupport import cookie_path
from OFS.Moniker import Moniker
from Products.CMFPlone.utils import safe_unicode
from plone import api
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from ploneintranet.workspace.browser.cart_actions.base import BaseCartView


class CutView(BaseCartView):
    """Cut Action implementation that performs "cut" on the items in cart."""

    def __call__(self):
        """Cut all items currently in cart and add them to clipboard.

        The tricky part here is that the method that Plone uses
        (manage_cutObjects) was only ment to work on objects of the same
        parent. However, our use case allows cutting objects of different
        parents. Hence we need to go one level deeper and reimplement some
        stuff that manage_cutObjects does in our own way.

        """

        request = self.request
        obj_list = []
        cannot_cut = []
        for obj in self.items:
            if obj:
                is_allowed = api.user.has_permission(
                    'Delete objects', obj=obj)
                is_locked = obj.wl_isLocked()
                is_movable = obj.cb_isMoveable()
                can_cut = is_allowed and is_movable and not is_locked
                if can_cut:
                    m = Moniker(obj)
                    obj_list.append(m.dump())
                else:
                    cannot_cut.append(u'"%s"' % safe_unicode(obj.Title()))

        if obj_list:
            # now store cutdata into a cookie
            # TODO: what if there's nothing in the list?
            ct_data = (1, obj_list)
            ct_data = _cb_encode(ct_data)  # probably means "clipboard encode"?

            response = request.response
            path = '{0}'.format(cookie_path(request))
            response.setCookie('__cp', ct_data, path=path)
            request['__cp'] = ct_data

            msg = _(
                u"batch_cut_success",
                default=u"${num_elems} Files were cut and moved to your cloud clipboard.",  # noqa
                mapping={"num_elems": len(obj_list)}
            )
            api.portal.show_message(
                message=msg,
                request=request,
                type="info",
            )

        if cannot_cut:
            msg = _(
                u"batch_cut_failure",
                default=u"The following items could not be cut: ${num_elems}",
                mapping={"num_elems": ', '.join(sorted(cannot_cut))}
            )
            api.portal.show_message(
                message=msg,
                request=request,
                type="info",
            )

        self.request.response.redirect(self.context.absolute_url())
