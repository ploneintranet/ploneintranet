# -*- coding: utf-8 -*-
from plone import api
from plone.app.layout.viewlets import common as base
from plone.memoize.view import memoize
from ploneintranet import api as pi_api
from ploneintranet.layout.app import apps_container_id


class MessagesViewlet(base.ViewletBase):
    """Display unread messages counter in topbar
    """

    @memoize
    def unread(self):
        try:
            return pi_api.messaging.get_inbox().new_messages_count
        except KeyError:
            # not even an inbox
            return 0

    def digits(self):
        return len(str(self.unread()))

    @property
    def apps_container_url(self):
        portal = api.portal.get()
        apps_container = getattr(portal, apps_container_id)
        return apps_container.absolute_url()
