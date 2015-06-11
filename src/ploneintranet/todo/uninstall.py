# -*- coding: utf-8 -*-
from plone import api


def uninstall(context):
    marker = 'ploneintranet.todo_uninstall.txt'
    if context.readDataFile(marker) is None:
        return

    # Delete roles
    portal = api.portal.get()
    valid_roles = portal.valid_roles()
    pas = api.portal.get_tool('acl_users')
    portal_role_manager = pas.portal_role_manager
    roles = portal_role_manager.listRoleIds()
    for role in ['Assignee']:
        if role in roles:
            portal_role_manager.removeRole(role)
        if role in valid_roles:
            portal._delRoles([role, ])
