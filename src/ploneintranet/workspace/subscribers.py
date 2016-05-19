import logging
from zope.annotation.interfaces import IAnnotations
from AccessControl.SecurityManagement import newSecurityManager
from collective.workspace.interfaces import IWorkspace
from plone import api
from plone.api.exc import PloneApiError
from Products.CMFPlacefulWorkflow.PlacefulWorkflowTool \
    import WorkflowPolicyConfig_id
from zope.globalrequest import getRequest
from ploneintranet.workspace import workspacefolder
from ploneintranet.workspace.behaviors.group import IMembraneGroup
from ploneintranet.workspace.case import ICase
from ploneintranet.workspace.utils import get_storage
from ploneintranet.workspace.utils import parent_workspace
from ploneintranet.workspace.unrestricted import execute_as_manager
from ploneintranet.workspace.config import INTRANET_USERS_GROUP_ID
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from ploneintranet.workspace.interfaces import IGroupingStoragable
from ploneintranet.workspace.interfaces import IGroupingStorage
from OFS.interfaces import IObjectWillBeRemovedEvent
from zope.component import getAdapter
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from Acquisition import aq_base
from OFS.CopySupport import cookie_path
from zExceptions import BadRequest

log = logging.getLogger(__name__)

WORKSPACE_INTERFACE = 'collective.workspace.interfaces.IHasWorkspace'


def workspace_state_changed(ob, event):
    """
    when a workspace is made 'open', we need to
    give all intranet users the 'Guest' role

    equally, when the workspace is not open, we need
    to remove the role again
    """
    workspace = event.object
    roles = ['Guest', ]
    if event.new_state.id == 'open':
        api.group.grant_roles(
            groupname=INTRANET_USERS_GROUP_ID,
            obj=workspace,
            roles=roles,
        )
        workspace.reindexObjectSecurity()
    elif event.old_state.id == 'open':
        api.group.revoke_roles(
            groupname=INTRANET_USERS_GROUP_ID,
            obj=workspace,
            roles=roles,
        )
        workspace.reindexObjectSecurity()


def workspace_added(ob, event):
    """
    when a workspace is created, we add the creator to
    the admin group. We then setup our placeful workflow

    """
    # Whoever creates the workspace should be added as an Admin
    # When copying a template, that is the current user
    # (not the one who created the original template)
    userid = api.user.get_current().id
    ob.setCreators([userid])
    IWorkspace(ob).add_to_team(
        user=userid,
        groups=set(['Admins']),
    )
    # During workspace creation, various functions
    # are called (renaming / workflow transitions) which do
    # low-level AccessControl checks.
    # Unfortunately these checks never re-ask PAS for a user's roles
    # or groups during a request, so we have to manually re-initialise
    # the security context for the current user.
    # ref: https://github.com/ploneintranet/ploneintranet/pull/438
    IAnnotations(ob.REQUEST)[('workspaces', userid)] = None
    acl_users = api.portal.get_tool('acl_users')
    user = acl_users.getUserById(userid)
    if user is not None:
        # NB when copying a template with execute_as_manager
        # this is 'finally' replaced again
        newSecurityManager(None, user)

    if ICase.providedBy(ob):
        """Case Workspaces have their own custom workflows
        """
        return

    # Configure our placeful workflow
    cmfpw = 'CMFPlacefulWorkflow'

    try:
        ob.manage_addProduct[cmfpw].manage_addWorkflowPolicyConfig()
    except BadRequest:
        # 'The id ".wf_policy_config" is invalid - it is already in use.'
        # copying a template workspace which already has a policy defined
        return

    # Set the policy for the config
    pc = getattr(ob, WorkflowPolicyConfig_id)
    pc.setPolicyIn('')
    pc.setPolicyBelow('ploneintranet_policy')


def invitation_accepted(event):
    """
    When an invitation is accepted, add the user to the team
    """
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


def _update_workspace_groupings(obj, event):
    """ If the relevant object is inside a workspace, the workspace grouping
        parameters (for the sidebar) need to be updated.
    """
    parent = parent_workspace(obj)
    if parent is None or not IGroupingStoragable.providedBy(parent):
        return

    storage = getAdapter(parent, IGroupingStorage)
    if IObjectRemovedEvent.providedBy(event) or \
            IObjectWillBeRemovedEvent.providedBy(event):
        storage.remove_from_groupings(obj)
    else:
        storage.update_groupings(obj)


def content_object_added_to_workspace(obj, event):
    _update_workspace_groupings(obj, event)


def content_object_edited_in_workspace(obj, event):
    _update_workspace_groupings(obj, event)


def content_object_removed_from_workspace(obj, event):
    _update_workspace_groupings(obj, event)


def content_object_moved(obj, event):
    # ignore if oldParent or newParent is None or if obj has just
    # been created or removed
    if event.oldParent is None or event.newParent is None:
        return
    if aq_base(event.oldParent) is aq_base(event.newParent):
        return
    if IGroupingStoragable.providedBy(event.oldParent):
        old_storage = getAdapter(event.oldParent, IGroupingStorage)
        old_storage.remove_from_groupings(obj)
    if IGroupingStoragable.providedBy(event.newParent):
        new_storage = getAdapter(event.newParent, IGroupingStorage)
        new_storage.update_groupings(obj)
    # Since OFS.CopySupport.manage_pasteObjects is called without a REQUEST
    # parameter, cb_dataValid() will still be true, because __cp will not
    # be reset. We do that manually here, so that the "paste" action will
    # disappear from the action list.
    request = getattr(obj, 'REQUEST', None)
    if request:
        request['RESPONSE'].setCookie(
            '__cp', 'deleted',
            path='%s' % cookie_path(request),
            expires='Wed, 31-Dec-97 23:59:59 GMT')
        request['__cp'] = None


def update_todo_state(obj, event):
    """
    After editing a Todo item, set the workflow state to either Open or Planned
    depending on the state of the Case.

    """
    # Do nothing on copy
    if IObjectCopiedEvent.providedBy(event):
        return
    obj.set_appropriate_state()
    obj.reindexObject()


def handle_case_workflow_state_changed(obj, event):
    """
    When the workflow state of a Case changes, perform the following actions:
    * Update the contained Todo items ans set adjust their workflow state
    * Grant assignees on tasks of the current milestone guest access
    """
    _update_todos_state(obj)
    _update_case_access(obj)


def _update_todos_state(obj):
    """
    Update the workflow state of Todo items in a Case, when the workflow state
    of the Case is changed.
    """
    pc = api.portal.get_tool('portal_catalog')
    current_path = '/'.join(obj.getPhysicalPath())
    brains = pc(path=current_path, portal_type='todo')
    for brain in brains:
        todo = brain.getObject()
        execute_as_manager(_update_todo_state, todo)


def _update_todo_state(todo):
    todo.set_appropriate_state()
    todo.reindexObject()


def _update_case_access(obj):
    execute_as_manager(obj.update_case_access)


def workspace_groupbehavior_toggled(obj, event):
    # If the IMembraneGroup behavior gets set or deactivated for workspaces,
    # the membrane tool needs to be updated, and all workspaces need to be
    # reindexed
    if obj.id != workspacefolder.__name__:
        return
    relevant_change = False
    for description in event.descriptions:
        if getattr(description, 'attribute', None) == 'behaviors':
            relevant_change = True
            break
    if not relevant_change:
        return
    try:
        membrane_tool = api.portal.get_tool('membrane_tool')
    # In case the membrane_tool cannot be found, just return.
    # This can happen in test scenarios that do not set up the full stack of
    # PloneIntranet.
    except PloneApiError, exc:
        log.error(exc)
        return
    if IMembraneGroup.__identifier__ in obj.behaviors:
        # The behavior was activated
        # Add the type to the membrane types and reindex all workspaces
        types = set(membrane_tool.membrane_types)
        types.add(workspacefolder.__name__)
        log.info("Enabling IMembraneGroup on %s", workspacefolder.__name__)
        membrane_tool.membrane_types = list(types)
    else:
        # The behavior was deactivated
        # Remove the type from the membrane types and reindex all workspaces
        types = [
            typ for typ in membrane_tool.membrane_types if
            typ != workspacefolder.__name__]
        log.info("Disabling IMembraneGroup on %s", workspacefolder.__name__)
        membrane_tool.membrane_types = types
    catalog = api.portal.get_tool('portal_catalog')
    membrane_catalog = membrane_tool._catalog
    for result in catalog(portal_type=workspacefolder.__name__):
        workspace = result.getObject()
        workspace.reindexObject()
        membrane_catalog.reindexObject(workspace)
