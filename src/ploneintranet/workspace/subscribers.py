from collective.workspace.interfaces import IWorkspace
from plone import api
from Products.CMFPlacefulWorkflow.PlacefulWorkflowTool \
    import WorkflowPolicyConfig_id


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
