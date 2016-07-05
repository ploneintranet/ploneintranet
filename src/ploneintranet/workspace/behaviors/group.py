# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.CMFPlone.utils import safe_unicode
from Products.PlonePAS.sheet import MutablePropertySheet
from Products.membrane.interfaces import IGroup
from Products.membrane.interfaces import IMembraneUserGroups
from Products.membrane.interfaces import IMembraneGroupProperties
from collective.workspace.interfaces import IWorkspace
from collective.workspace.pas import WORKSPACE_INTERFACE
from dexterity.membrane.behavior.group import MembraneGroup
from dexterity.membrane.behavior.user import DxUserObject
from plone import api
from zope.interface import Interface
from zope.component import adapter
from zope.interface import implementer


class IMembraneGroup(Interface):
    """Marker interface for Membrane Group"""


@implementer(IGroup)
@adapter(IMembraneGroup)
class MembraneWorkspaceGroup(object):

    def __init__(self, context):
        self.context = context

    def getGroupId(self):
        return self.context.getId()

    def getGroupName(self):
        return self.context.title

    def getRoles(self):
        return ()

    def getGroupMembers(self):
        ws = IWorkspace(self.context)
        if not ws:
            return []
        return tuple(set([id for (id, details) in ws.members.items()]))


@implementer(IMembraneGroupProperties)
@adapter(IMembraneGroup)
class MembraneGroupProperties(MembraneGroup):
    """ Properties for our membrane group
    """

    def getPropertiesForUser(self, user, request=None):
        """Get properties for this group.

        """
        properties = {}
        catalog = api.portal.get_tool('portal_catalog')
        query = {
            'object_provides': WORKSPACE_INTERFACE,
            'getId': user.getId()}
        brains = catalog.unrestrictedSearchResults(query)
        # Pick the first result. Ignore potential catalog problems
        if len(brains):
            portal_path = api.portal.get().getPhysicalPath()
            brain = brains[0]
            ws_obj = brain._unrestrictedGetObject()
            properties['title'] = safe_unicode(brain.Title)
            properties['description'] = safe_unicode(brain.Description)
            path = '/' + '/'.join(ws_obj.getPhysicalPath()[len(portal_path):])
            properties['workspace_path'] = path
            properties['state'] = api.content.get_state(ws_obj)
            properties['uid'] = ws_obj.UID()
            properties['type'] = 'workspace'
            properties['portal_type'] = ws_obj.portal_type
            # We need to explicitly cast the type to a string type, since
            # the property sheet pukes on zope.i18nmessageid.message.Message
            typ = safe_unicode(ws_obj.Type()).encode('utf-8')
            properties['workspace_type'] = typ
        return MutablePropertySheet(self.context.getId(), **properties)

    def setPropertiesForUser(self, user, propertysheet):
        """
        Set modified properties on the group persistently.
        Currently, we do nothing, since all properties are handled via
        directly editing the workspace properties
        """
        pass

    def deleteUser(self, user_id):
        """
        Remove properties stored for a user

        Note that membrane itself does not do anything here.  This
        indeed seems unneeded, as the properties are stored on the
        content item, so they get removed anyway without needing
        special handling.
        """
        pass


class IGroupsProvider(Interface):
    """
    Marks the object as a Membrane groups provider using a simple
    iteration over all workspaces that the user is a member of
    """


@implementer(IMembraneUserGroups)
@adapter(IGroupsProvider)
class MembraneWorkspaceGroupsProvider(DxUserObject):
    """
    Determine the groups to which a principal belongs.
    A principal can be a user or a group.

    This is a plugin provider, used by PAS. When the groups of a user
    are determined, this is roughly the call flow:

    The main method that plays a role is
    `Products.PluggableAuthService.PluggableAuthService.PluggableAuthService.
        _getGroupsForPrincipal`.
    This method iterates over all plugins that are registered as groupmakers
    (= they implement `IGroupsPlugin`). Among those plugins are source_groups
    and auto_group, and also our workspace_groups plugin from
    `collective.workspace.pas.WorkspaceGroupManager`.

    But in this case, the membrane_groups plugin is the one we are interested
    in. In `Products.membrane.plugins.groupmanager.getGroupsForPrincipal`
    the providers that can be used for looking up the group memberships of the
    principal are found via a call to `findMembraneUserAspect` of
    Products.membrane.utils.
    It does a catalog query for all objects that implement
    `user_ifaces.IMembraneUserGroups` and fulfill the query (exact match of the
    user id). Then it applies this interface to the results and returns them.
    This is why this provider needs to announce that it provides the interface
    `Products.membrane.interfaces.user.IMembraneUserGroups`
    for membrane user objects `dexterity.membrane.behavior.user.IMembraneUser`.
    Otherwise this provider will not be found by the membrane_plugin when it
    is handling a user.

    Note: this plugin provider should also be able to handle the lookup of
    which groups a group is a member of (= case: principal is a group).
    With the current implementation of Products.membrane, this is not possible.
    See quaive/ploneintranet#415 for a discussion of this.
    """

    security = ClassSecurityInfo()

    def _iterWorkspaces(self, userid=None):
        catalog = api.portal.get_tool('portal_catalog')
        query = {'object_provides': WORKSPACE_INTERFACE}
        if userid:
            query['workspace_members'] = userid
        return (b.id for b in catalog.unrestrictedSearchResults(query))

    def _build_groups(self, principal_id, groups=None):
        """Build a set of groups recursively.

        The groups variable is passed around recursively.
        """
        if groups is None:
            groups = set()
        for workspace in self._iterWorkspaces(principal_id):
            if workspace in groups:
                # We must watch out and prevent this:
                # RuntimeError: maximum recursion depth exceeded in cmp
                continue
            groups.add(workspace)
            # Recursive: get the groups of the groups.
            self._build_groups(workspace, groups)
        return groups

    # IGroupsPlugin implementation
    def getGroupsForPrincipal(self, principal, request=None):
        return tuple(self._build_groups(principal.getId()))
    security.declarePrivate('getGroupsForPrincipal')
