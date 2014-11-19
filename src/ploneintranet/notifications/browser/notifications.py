# -*- coding: utf-8 -*-
# from AccessControl import Unauthorized
# from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
# from plone import api


class NotificationsView(BrowserView):

    def your_messages(self):
        # count to show unread messages
        # user = api.user.get_current()
        display_message = []
        return display_message
