# -*- coding: utf-8 -*-
"""Download cart for batch processing of items. Parts taken from slc.cart"""

import re
from OFS.CopySupport import CopyError
from ZODB.POSException import ConflictError
from plone import api
from zope.annotation.interfaces import IAnnotations
from zope.component import getAdapter
from zope.component import getAdapters
from zope.interface import Attribute
from zope.interface import implements
from zope.interface import Interface
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import IPublishTraverse
from zExceptions import NotFound
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa

import logging

log = logging.getLogger(__name__)

ALLOWED_VIA_URL = [
    'item_count',
    'clear',
]
"""Attributes that we allow to be traversable via URL."""


class NoResultError(Exception):
    """Exception if catalog returns zero results."""


class ICartAction(Interface):
    """Specification of what a Cart Action needs to provide."""

    name = Attribute('Short id if the action, used in URLs, lookups, etc.')
    title = Attribute('User friendly title of the Cart Action.')
    weight = Attribute('An integer used for sorting the actions.')

    def run():
        """Perform the action."""


class Cart(BrowserView):
    """A BrowserView for managing a cart."""

    implements(IPublishTraverse)

    action = None

    def publishTraverse(self, request, name):  # noqa
        """A custom publishTraverse method.

        This enables us to use URL traversal to run cart actions. Examples:
        @@cart/delete, @@cart/download, etc. URL access is only allowed for
        attributes listed in ALLOWED_VIA_URL.

        """
        if name in ALLOWED_VIA_URL:
            return getattr(self, name)
        else:
            self.action = name
            return getattr(self, '_run_action')

    ##################
    # Helper methods #
    ##################

    @property
    def cart(self):
        """Return a list of items currently in cart.

        Also initialize the cart along the way if necessary.

        :return: list of UUIDs of all the items in cart
        :rtype: list of strings
        """
        # get the zope.annotations object stored on current member object
        annotations = IAnnotations(api.user.get_current())
        return annotations.setdefault('cart', set())

    def _get_brain_by_uid(self, uid):
        """Return portal_catalog brains metadata of an item with the specified
        UID.

        :param UID: Unique ID of an item.
        :type UID: string
        :returns: Brain (metadata) of item of passed UID.
        :rtype: Brain

        """
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(UID=uid)

        return brains[0] if brains else None

    def _run_action(self):
        """Run a cart action.

        :param name: name of the action
        :type name: string
        :return: (nothing)
        """
        if self.action not in [name for name, action in self.actions]:
            raise NotFound()
        action = getAdapter(self.context, ICartAction, name=self.action)
        return action.run()

    def _clear(self):
        """Remove all items from cart and redirect back to @@cart view.

        :return: redirect to @@cart
        """
        annotations = IAnnotations(api.user.get_current())
        annotations['cart'] = set()

    @property
    def items(self):
        """Return metadata about items currently in cart.

        :return: Return Brains (metadata) of items in user's cart.
        :rtype: list of Brains
        """
        items = []
        for UID in self.cart:
            brain = self._get_brain_by_uid(UID)
            if brain:
                items.append(brain)
            else:
                msg = "An item in cart (UID: {0}) not found in the catalog."
                log.warn(NoResultError(msg.format(UID)))

        return items

    @property
    def actions(self):
        """Get a sorted list of actions users can perform on cart items.

        Actions are sorted by their weight attribute in ascending order.

        :return: Actions that users can perform on cart items.
        :rtype: sorted list of (name, action) tuples
        """
        actions = getAdapters((self.context, ), ICartAction)
        return sorted(actions, key=lambda action: action[1].weight)

    #######################
    # Interaction methods #
    #######################

    def __call__(self):
        cart_items = self.request.form.get("cart_items", [])
        if isinstance(cart_items, str):
            cart_items = [cart_items]

        self._clear()
        for item in cart_items:
            item = item.strip()
            if item:
                self.cart.add(item)

        self.action = self.request.form.get("batch-function", False)
        if self.action is False:
            return self

        if type(self.action) == list:
            self.action = [x for x in self.action if x.strip()].pop()
        if self.action != '' and self.action != 'download' and \
           self.action != 'paste':
            # We don't care about any output. The relevant information will
            # be insde a portal status message anyway.
            self._run_action()
        if self.action == 'download' and not cart_items:
            self.action = 'none'
            api.portal.show_message(
                message="No items selected to download.",
                request=self.request,
                type="warning")
        elif self.action == 'paste':
            try:
                self.context.manage_pasteObjects(REQUEST=self.request)
            except CopyError, ce:
                message = re.sub('<[^>]*>|\n', ' ', ce.message)
                message = re.sub('\s{2,}', ' ', message).strip()
                api.portal.show_message(
                    message=message,
                    request=self.request,
                    type="warning")
            except ConflictError:
                api.portal.show_message(
                    message=_(u'Error while pasting items'),
                    request=self.request,
                    type="error")
            else:
                api.portal.show_message(
                    message="Item(s) pasted",
                    request=self.request,
                    type="success")

        self.request.response.redirect(
            '{0}/?{1}=1&suppress_message=1'.format(
                self.context.absolute_url(), self.action))
