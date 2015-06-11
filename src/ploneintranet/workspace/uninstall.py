# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.workspace.config import DYNAMIC_GROUPS_PLUGIN_ID
from ploneintranet.workspace.config import INTRANET_USERS_GROUP_ID


def uninstall(context):
    """
    - remove the global "workspaces" container?
    - remove the acl user group that holds all intranet users?
    - remove the dynamic groups plugin?
    - unset the ploneintranet_policy for all addable types?
    """
    marker = 'ploneintranet.workspace_uninstall.txt'
    if context.readDataFile(marker) is None:
        return

    # Remove group that holds all intranet users
    if api.group.get(groupname=INTRANET_USERS_GROUP_ID):
        api.group.delete(groupname=INTRANET_USERS_GROUP_ID)

    # Remove dynamic groups plugin to put all users into the above group
    pas = api.portal.get_tool('acl_users')
    if DYNAMIC_GROUPS_PLUGIN_ID in pas.objectIds():
        pas.manage_delObjects([DYNAMIC_GROUPS_PLUGIN_ID])
