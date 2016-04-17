# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.membrane.interfaces import IGroup
from Products.membrane.interfaces import IMembraneUserGroups
from collective.workspace.interfaces import IWorkspace
from collective.workspace.pas import WORKSPACE_INTERFACE
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


class IGroupsProvider(Interface):
    """
    Marks the object as a Membrane groups provider using a simple
    iteration over all workspaces that the user is a member of
    """


@implementer(IMembraneUserGroups)
@adapter(IGroupsProvider)
class MembraneWorkspaceGroupsProvider(DxUserObject):
    """
    Adapts from IGroupsProvider to IMembraneUserGroups
    """

    security = ClassSecurityInfo()

    def _iterWorkspaces(self, userid=None):
        catalog = api.portal.get_tool('portal_catalog')
        query = {'object_provides': WORKSPACE_INTERFACE}
        if userid:
            query['workspace_members'] = userid
        workspaces = [b.id for b in catalog.unrestrictedSearchResults(query)]
        return iter(workspaces)

    # IGroupsPlugin implementation
    def getGroupsForPrincipal(self, principal, request=None):
        groups = set()
        for workspace in self._iterWorkspaces(principal.getId()):
            groups.add(workspace)
        return tuple(groups)
    security.declarePrivate('getGroupsForPrincipal')
