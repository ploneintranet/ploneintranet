# -*- coding: utf-8 -*-
from plone import api
from Products.Five import BrowserView
from Products.PlonePAS.interfaces.group import IGroupData


class WorkspaceGroupView(BrowserView):
    """Helper view to show the members of a group when clicked in workspace"""

    def group_details(self):
        """ Get group data """
        gid = self.request.get('id')
        if not gid:
            return dict(
                id='', title=u"No Group", description=u"", members=[])

        group = api.group.get(groupname=gid)
        g_title = group.getProperty('title') or group.getId() or gid
        g_description = group.getProperty('description')

        users = api.user.get_users(groupname=gid)
        members = []
        for principal in users:
            id = principal.getId()
            if IGroupData.providedBy(principal):
                typ = 'group'
                title = principal.getProperty('title') or id
                path = principal.getProperty('workspace_path') or ''
            else:
                typ = 'user'
                title = principal.getProperty('fullname') or id
                path = '/profiles/{0}'.format(id)
            members.append(dict(id=id, title=title, typ=typ, path=path))

        return dict(
            id=gid, title=g_title, description=g_description, members=members
        )
