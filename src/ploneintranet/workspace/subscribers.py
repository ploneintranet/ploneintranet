from collective.workspace.interfaces import IWorkspace
from Products.CMFPlacefulWorkflow.PlacefulWorkflowTool \
    import WorkflowPolicyConfig_id


def workspace_added(ob, event):
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
