# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
from plone import api


class Users(BrowserView):

    index = ViewPageTemplateFile('panel_users.pt')

    def users(self):
        """Get users.

        Applies very basic user name searching
        """
        users = api.user.get_users()

        search_string = self.request.form.get('usersearch')
        if search_string:
            search_string = search_string.lower()
            users = filter(
                lambda x: search_string in x.getProperty('fullname').lower(),
                users
            )

        return users
