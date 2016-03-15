# -*- coding: utf-8 -*-
from OFS.CopySupport import _cb_encode
from OFS.CopySupport import cookie_path
from OFS.Moniker import Moniker
from plone import api
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
        for obj in self.items:
            if obj and obj.cb_isMoveable() and not obj.wl_isLocked():
                m = Moniker(obj)
                obj_list.append(m.dump())
        # now store cutdata into a cookie
        # TODO: what if there's nothing in the list?
        ct_data = (1, obj_list)
        ct_data = _cb_encode(ct_data)  # probably means "clipboard encode"?

        response = request.response
        path = '{0}'.format(cookie_path(request))
        response.setCookie('__cp', ct_data, path=path)
        request['__cp'] = ct_data

        api.portal.show_message(
            message=(
                "{0} Files were cut and moved to your cloud clipboard."
            ).format(len(obj_list)),
            request=request,
            type="info",
        )
        self.request.response.redirect(self.context.absolute_url())
