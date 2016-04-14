# -*- coding: utf-8 -*-
from Products.membrane.interfaces import IGroup
from collective.workspace.interfaces import IWorkspace
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
