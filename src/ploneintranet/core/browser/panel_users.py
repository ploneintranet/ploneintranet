# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api


class Users(BrowserView):

    index = ViewPageTemplateFile('panel_users.pt')
    input_name = 'users:list'
    input_type = 'checkbox'
    panel_id = 'panel-users'
    panel_type = 'mentions'

    def users(self):
        '''Get users.

        Applies very basic user name searching
        '''
        users = api.user.get_users()

        search_string = self.request.form.get('usersearch')
        if search_string:
            search_string = search_string.lower()
            users = filter(
                lambda x: search_string in x.getProperty('fullname').lower(),
                users
            )
        return users


class User(Users):

    index = ViewPageTemplateFile('panel_users.pt')
    input_name = 'user'
    input_type = 'radio'
    panel_id = 'panel-user'
    panel_type = 'user'
