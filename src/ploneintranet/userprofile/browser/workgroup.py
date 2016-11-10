# coding=utf-8
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.memoize.view import memoize
from ploneintranet import api as pi_api
from Products.Five import BrowserView
from zope.interface import implements


class WorkGroupView(BrowserView):
    implements(IBlocksTransformEnabled)
    """View for user profile."""

    my_groups = my_workspaces = []

    _default_tabs = (
        u'group-view',
    )

    @property
    @memoize
    def groups_container(self):
        ''' Returns the group container (if found) or an empty dictionary
        '''
        portal = api.portal.get()
        return portal.get('groups', {})

    @property
    @memoize
    def users_container(self):
        ''' Returns the group container (if found) or an empty dictionary
        '''
        portal = api.portal.get()
        return portal.get('profiles', {})

    @property
    @memoize
    def userids(self):
        ''' Return the member ids that are in the user profile container
        '''
        container = self.users_container
        return [
            key for key in self.context.members
            if key in container
        ]

    @property
    @memoize
    def users(self):
        ''' Return the user that are in the user profile container
        '''
        container = self.users_container
        keys = self.userids
        return [container[key] for key in keys]

    @property
    @memoize
    def groupids(self):
        ''' Return the group ids that are in the group container
        '''
        container = self.groups_container
        return [
            key for key in self.context.members
            if key in container
        ]

    @property
    @memoize
    def groups(self):
        ''' Return the groups that are in the group container
        '''
        container = self.groups_container
        keys = self.groupids
        return [container[key] for key in keys]

    def get_avatar_tag(self, userid):
        ''' Provide HTML tag to display the avatar
        '''
        return pi_api.userprofile.avatar_tag(
            username=userid
        )
