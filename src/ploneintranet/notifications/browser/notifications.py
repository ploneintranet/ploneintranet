# -*- coding: utf-8 -*-
# from AccessControl import Unauthorized
# from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from ploneintranet.notifications.channel import AllChannel


class NotificationsView(BrowserView):

    def your_notifications(self):
        # count to show unread messages
        user = api.user.get_current()
        #import ipdb; ipdb.set_trace()
        display_message = []
        channel = AllChannel(user)
        #display_message = channel.get_all_messages()
        display_message = channel.get_unread_messages()
        return display_message
