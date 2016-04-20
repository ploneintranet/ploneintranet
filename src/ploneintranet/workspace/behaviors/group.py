# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.CMFPlone.utils import safe_unicode
from Products.PlonePAS.sheet import MutablePropertySheet
from Products.membrane.interfaces import IGroup
from Products.membrane.interfaces import IMembraneUserGroups
from Products.membrane.interfaces import IMembraneUserProperties
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


@implementer(IMembraneUserProperties)
@adapter(IMembraneGroup)
class MembraneGroupProperties(DxUserObject):
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
        workspaces = catalog.unrestrictedSearchResults(query)
        # Pick the first result. Ignore potential catalog problems
        if len(workspaces):
            workspace = workspaces[0]
            properties['title'] = safe_unicode(workspace.Title)
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
