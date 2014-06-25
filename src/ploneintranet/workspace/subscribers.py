from collective.workspace.interfaces import IWorkspace
from plone import api
from Products.CMFPlacefulWorkflow.PlacefulWorkflowTool \
    import WorkflowPolicyConfig_id
from zope.globalrequest import getRequest

from ploneintranet.workspace.utils import get_storage
from ploneintranet.workspace import MessageFactory as _


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
    old_group_name = workspace.group_for_policy(event.old_policy)
    old_group = api.group.get(old_group_name)
    for member in old_group.getAllGroupMembers():
        groups = workspace.get(member.getId()).groups
        groups -= set([event.old_policy.title()])
        groups.add(event.new_policy.title())


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
                        _('Oh boy, oh boy, you are already a member'),
                        request,
                    )
                    break
        else:
            ws.add_to_team(user=username)
            api.portal.show_message(
                _('Welcome to our family, Stranger'),
                request,
            )
