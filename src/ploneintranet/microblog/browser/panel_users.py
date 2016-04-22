# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ploneintranet import api as pi_api
from plone.memoize.view import memoize_contextless


class Users(BrowserView):

    index = ViewPageTemplateFile('templates/panel_users.pt')
    input_name = 'users:list'
    input_type = 'checkbox'
    panel_id = 'panel-users'
    panel_type = 'mentions'

    user_ids = []
    selected_users = []
    selected_user_ids = []

    @property
    @memoize_contextless
    def selected_users(self):
        ''' Returns the selected users
        according to the "mentions" parameter in the request
        '''
        user_generator = pi_api.userprofile.get_users(
            getId=self.request.form.get('mentions', []),
        )
        return list(user_generator)

    @property
    @memoize_contextless
    def selected_user_ids(self):
        ''' Returns the selected user ids
        according to the "mentions" parameter in the request
        '''
        return [user.id for user in self.selected_users]

    @property
    @memoize_contextless
    def users(self):
        '''Get the users that survice the usersearch filter.

        Users are sorted on fullname
        '''
        usersearch = '*%s*' % self.request.form.get('usersearch', '')
        usersearch = usersearch.replace('**', '')
        users = pi_api.userprofile.get_users(
            SearchableText=usersearch,
        )
        return sorted(users, key=lambda x: x.fullname)

    @property
    @memoize_contextless
    def user_ids(self):
        ''' Returns the filtered user ids sorted by id
        '''
        return sorted([user.id for user in self.users])


class User(Users):

    index = ViewPageTemplateFile('templates/panel_users.pt')
    input_name = 'user'
    input_type = 'radio'
    panel_id = 'panel-user'
    panel_type = 'user'
