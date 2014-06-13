from collective.workspace.interfaces import IWorkspace
from plone import api
from Products.CMFPlacefulWorkflow.PlacefulWorkflowTool \
    import WorkflowPolicyConfig_id
from zope.globalrequest import getRequest

from ploneintranet.workspace.utils import get_storage


WORKSPACE_INTERFACE = 'collective.workspace.interfaces.IHasWorkspace'


def workspace_added(ob, event):
    """
    when a workspace is created, we add the creator to
    the admin group. We then setup our placeful workflow

    """
    # Whoever creates the workspace should be added as an Admin
    creator = ob.Creator()
    IWorkspace(ob).add_to_team(
        user=creator,
        groups=set(['Admins']),
    )

    # Configure our placeful workflow
    cmfpw = 'CMFPlacefulWorkflow'
    ob.manage_addProduct[cmfpw].manage_addWorkflowPolicyConfig()

    # Set the policy for the config
    pc = getattr(ob, WorkflowPolicyConfig_id)
    pc.setPolicyIn('')
    pc.setPolicyBelow('ploneintranet_policy')


def participation_policy_changed(ob, event):
    """ Move all the existing users to a new group """
    workspace = IWorkspace(ob)
    old_group_name = "%s:%s" % (event.old_policy, ob.UID())
    old_group = api.group.get(old_group_name)
    for member in old_group.getAllGroupMembers():
        groups = workspace.get(member.getId()).groups
        groups -= set([event.old_policy])
        groups.add(event.new_policy)


def invitation_accepted(event):
    request = getRequest()
    storage = get_storage()
    if event.token_id not in storage:
        return

    ws_uid, username = storage[event.token_id]
    storage[event.token_id]
    acl_users = api.portal.get_tool('acl_users')
    acl_users.updateCredentials(
        request,
        request.response,
        username,
        None
    )
    catalog = api.portal.get_tool(name="portal_catalog")
    brain = catalog.unrestrictedSearchResults(UID=ws_uid)[0]
    with api.env.adopt_roles(["Manager"]):
        ws = IWorkspace(brain.getObject())
        for name in ws.members:
            member = api.user.get(username=name)
            if member is not None:
                if member.getUserName() == username:
                    api.portal.show_message(
                        'Oh boy, oh boy, you are already a member',
                        request,
                    )
                    break
        else:
            ws.add_to_team(user=username)
            api.portal.show_message(
                'Welcome to our family, Stranger',
                request,
            )


def user_deleted_from_site_event(event):
    """ Remove deleted user from all the workspaces where he
    is a member """
    userid = event.principal

    catalog = api.portal.get_tool('portal_catalog')
    query = {'object_provides': WORKSPACE_INTERFACE}

    query['workspace_members'] = userid
    workspaces = [
        IWorkspace(b._unrestrictedGetObject())
        for b in catalog.unrestrictedSearchResults(query)
        ]
    for workspace in workspaces:
        workspace.remove_from_team(userid)
