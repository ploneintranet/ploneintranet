# -*- coding: utf-8 -*-
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api

from zope.component import getUtility

from plonesocial.messaging.interfaces import IMessagingLocator


class NotificationsViewlet(ViewletBase):

    index = ViewPageTemplateFile('notifications.pt')

    def number_of_messages(self):
        # return number of messages
        user = api.user.get_current()
        if not user:
            return None

        locator = getUtility(IMessagingLocator)
        inboxes = locator.get_inboxes()

        if user.id not in inboxes:
            return None

        messages = inboxes[user.id]
        return messages.new_messages_count
