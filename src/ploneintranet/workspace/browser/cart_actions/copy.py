# -*- coding: utf-8 -*-
from OFS.CopySupport import _cb_encode
from OFS.CopySupport import cookie_path
from OFS.Moniker import Moniker
from plone import api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.browser.cart_actions.base import BaseCartView


class CopyView(BaseCartView):
    """Copy Action implementation that copies items in cart to clipboard.

    The tricky part here is that the method that Plone uses
    (manage_copyObjects) was only ment to work on objects of the same
    parent. However, our use case allows copying objects of different
    parents. Hence we need to go one level deeper and reimplement some
    stuff that manage_copyObjects does in our own way.

    """

    def __call__(self):
        request = self.request
        obj_list = []
        for obj in self.items:
            if obj and obj.cb_isCopyable():
                m = Moniker(obj)
                obj_list.append(m.dump())
        # now store copydata into a cookie
        # TODO: what if there's nothing in the list?
        cp_data = (0, obj_list)
        cp_data = _cb_encode(cp_data)  # probably means "clipboard encode"?

        response = request.response
        path = '{0}'.format(cookie_path(request))
        response.setCookie('__cp', cp_data, path=path)
        request['__cp'] = cp_data

        msg = _(
            u"batch_copied_success",
            default=u"${num_elems} Files were copied to your cloud clipboard.",
            mapping={"num_elems": len(obj_list)}
        )
        api.portal.show_message(
            message=msg,
            request=request,
            type="info",
        )
        return self.index()
