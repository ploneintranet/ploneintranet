from ploneintranet.workspace.config import DYNAMIC_GROUPS_PLUGIN_ID
from ploneintranet.workspace.config import INTRANET_USERS_GROUP_ID
from ploneintranet.workspace.config import TEMPLATES_FOLDER
from plone import api

from Products.PluggableAuthService.plugins.DynamicGroupsPlugin \
    import addDynamicGroupsPlugin
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces


def post_install(context):
    """
    - adds the global "workspaces" container
    - adds the global "templates" case templates container
      (actual case template is provided by ploneintranet.suite)
    - sets an acl user group to hold all intranet users
    - setup the dynamic groups plugin
    - sets the addable types for the ploneintranet policy
    """
    marker = 'ploneintranet.workspace_default.txt'
    if context.readDataFile(marker) is None:
        return

    portal = api.portal.get()

    if 'workspaces' not in portal:
        api.content.create(
            container=portal,
            type='ploneintranet.workspace.workspacecontainer',
            title='Workspaces'
        )
    if TEMPLATES_FOLDER not in portal:
        api.content.create(
            container=portal,
            id=TEMPLATES_FOLDER,
            type='ploneintranet.workspace.workspacecontainer',
            title='Templates'
        )

    # Set up a group to hold all intranet users
    if api.group.get(groupname=INTRANET_USERS_GROUP_ID) is None:
        api.group.create(groupname=INTRANET_USERS_GROUP_ID)

    # Set up dynamic groups plugin to put all users into the above group
    pas = api.portal.get_tool('acl_users')
    if DYNAMIC_GROUPS_PLUGIN_ID not in pas.objectIds():
        addDynamicGroupsPlugin(
            pas,
            DYNAMIC_GROUPS_PLUGIN_ID,
            "ploneintranet.workspace Dynamic Groups"
        )
        plugin = pas[DYNAMIC_GROUPS_PLUGIN_ID]
        plugin.addGroup(
            group_id=INTRANET_USERS_GROUP_ID,
            predicate='python: True',
            title='All Intranet Users',
            description='',
            active=True,
        )
        # activate the plugin (all interfaces)
        activatePluginInterfaces(portal, DYNAMIC_GROUPS_PLUGIN_ID)

    # deactivate the enumerate groups interface for collective.workspace
    activatePluginInterfaces(portal, 'workspace_groups',
                             disable=['IGroupEnumerationPlugin'])

    # Set up the ploneintranet policy for all addable types
    # Re-run ploneintranet.workspace:default after installing extra types!
    default_types = []
    types = api.portal.get_tool('portal_types')
    for type_info in types.listTypeInfo():
        if type_info.global_allow:
            default_types.append(type_info.getId())

    if default_types:
        # Folders should be state-less!
        # Todo items use todo_workflow
        default_types = [
            x for x in default_types if x not in ('Folder', 'todo')]
        pwftool = api.portal.get_tool('portal_placeful_workflow')
        policy = pwftool['ploneintranet_policy']

        policy.setChainForPortalTypes(default_types, ('(Default)',))
