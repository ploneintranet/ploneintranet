# -*- coding: utf-8 -*-
from plone import api
from Products.Five import BrowserView
from Products.PlonePAS.interfaces.group import IGroupData
from ploneintranet import api as pi_api


class WorkspaceGroupView(BrowserView):
    """Helper view to show the members of a group when clicked in workspace"""

    def group_details(self):
        """ Get group data """
        gid = self.request.get('id')
        default = dict(id='',
                       title=u"No Group",
                       description=u"",
                       users=[],
                       groups=[])
        if not gid:
            return default
        group = api.group.get(groupname=gid)
        if group.getProperty('state') == 'secret':
            return default
        g_title = group.getProperty('title') or group.getId() or gid
        g_description = group.getProperty('description')

        members = api.user.get_users(groupname=gid)
        users = []
        groups = []
        for principal in members:
            id = principal.getId()
            if IGroupData.providedBy(principal):
                if principal.getProperty('state') == 'secret':
                    continue
                typ = 'group'
                title = principal.getProperty('title') or id
                path = principal.getProperty('workspace_path') or ''
                groups.append(dict(id=id, title=title, typ=typ, path=path))
            else:
                typ = 'user'
                title = principal.getProperty('fullname') or id
                path = '/profiles/{0}'.format(id)
                users.append(dict(id=id, title=title, typ=typ, path=path))

        return dict(
            id=gid, title=g_title, description=g_description, users=users,
            groups=groups
        )

    def get_avatar_tag(self, userid):
        ''' Provide HTML tag to display the avatar
        '''
        return pi_api.userprofile.avatar_tag(
            username=userid
        )
