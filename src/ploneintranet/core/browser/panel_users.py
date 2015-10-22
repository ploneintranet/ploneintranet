# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ploneintranet import api as pi_api


class Users(BrowserView):

    index = ViewPageTemplateFile('panel_users.pt')
    input_name = 'users:list'
    input_type = 'checkbox'
    panel_id = 'panel-users'
    panel_type = 'mentions'

    user_ids = []
    selected_users = []
    selected_user_ids = []

    def users(self):
        '''Get users.

        Applies very basic user name searching
        '''
        search_string = self.request.form.get('usersearch')
        users = [x for x in pi_api.userprofile.get_users()]
        self.selected_users = [
            pi_api.userprofile.get(uid)
            for uid in self.request.form.get('mentions', [])]
        self.selected_user_ids = [user.id for user in self.selected_users]
        if search_string:
            search_string = search_string.lower()
            users = filter(
                lambda x: search_string in x.fullname.lower(),
                users
            )
        self.user_ids = sorted([user.id for user in users])
        return sorted(users, cmp=lambda x, y:
                      cmp(x.fullname.lower(), y.fullname.lower()))


class User(Users):

    index = ViewPageTemplateFile('panel_users.pt')
    input_name = 'user'
    input_type = 'radio'
    panel_id = 'panel-user'
    panel_type = 'user'
