# -*- coding: utf-8 -*-
from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from plonesocial.messaging.interfaces import IMessagingLocator
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility


class NotificationsViewlet(ViewletBase):

    index = ViewPageTemplateFile('notifications.pt')

    def available(self):
        """Return True if the viewlet is available."""
        locator = getUtility(IMessagingLocator)
        inboxes = locator.get_inboxes()
        username = api.user.get_current().getUserName()
        if username in inboxes:
            conversation = inboxes[username]
            return conversation.new_messages_count > 0
        else:
            return False
