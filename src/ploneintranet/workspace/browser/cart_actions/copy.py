# -*- coding: utf-8 -*-
"""A Cart Action for deleting all items listed in cart."""

from OFS.CopySupport import _cb_encode
from OFS.CopySupport import cookie_path
from OFS.Moniker import Moniker
from plone import api

NAME = 'copy'
TITLE = u'Copy'
WEIGHT = 15


class CopyAction(object):
    """Copy Action implementation that copies items in cart to clipboard.

    The tricky part here is that the method that Plone uses
    (manage_copyObjects) was only ment to work on objects of the same
    parent. However, our use case allows copying objects of different
    parents. Hence we need to go one level deeper and reimplement some
    stuff that manage_copyObjects does in our own way.

    """

    name = NAME
    title = TITLE
    weight = WEIGHT

    def __init__(self, context):
        self.context = context

    def run(self):
        """Copy all items currently in cart to clipboard."""
        cart_view = self.context.restrictedTraverse('cart')
        request = self.context.REQUEST
        cart = cart_view.cart

        # create a list of "Monik-ed" object paths for those objects
        # that we will store into clipboard
        obj_list = []

        for obj_uuid in cart:
            obj = api.content.get(UID=obj_uuid)
            if obj is None:
                # An object that is in cart was apparently deleted by someone
                # else and dosn't exist anymore, so there's nothing to do.
                continue

            if not obj.cb_isCopyable():
                continue

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

        api.portal.show_message(
            message="{0} item(s) copied.".format(len(obj_list)),
            request=request,
            type="info")

        portal = api.portal.get()
        response.redirect(portal.absolute_url())
