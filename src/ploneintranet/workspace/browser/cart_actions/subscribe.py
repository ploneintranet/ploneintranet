# -*- coding: utf-8 -*-
"""A Cart Action for subscribing to all items listed in cart."""

from ploneintranet.workspace.browser.cart_actions.base import BaseCartView


class SubscribeView(BaseCartView):

    def __call__(self):
        """Subscribe to all items currently in cart
        """
        for obj in self.items:
            subscriber_view = obj.restrictedTraverse('subscribe')
            subscriber_view.subscribe(notifiers=['mail'])

        return self.index()
