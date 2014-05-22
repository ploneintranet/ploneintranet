from Products.CMFCore.interfaces import IContentish
from borg.localrole.default_adapter import DefaultLocalRoleAdapter
from borg.localrole.interfaces import ILocalRoleProvider
from collective.workspace.interfaces import IHasWorkspace
from collective.workspace.workspace import Workspace
from plone import api
from zope.interface import implements
from zope.component import adapts


class PloneIntranetWorkspace(Workspace):
    """
    A custom workspace behaviour, based on collective.workspace

    Here we define our own available groups, and the roles
    they are given on the workspace.
    """

    # A list of groups to which team members can be assigned.
    # Maps group name -> roles
    available_groups = {
        u'Members': ('Reader', 'TeamMember'),
        u'Admins': ('Contributor', 'Editor', 'Reviewer',
                    'Reader', 'TeamManager',),
        u'Consumers': ('Reader',),
        u'Producers': ('Reader', 'Contributor',),
        u'Publishers': ('Reader', 'Contributor', 'SelfPublisher',),
        u'Moderators': ('Reader', 'Contributor', 'Reviewer', 'Editor',),
    }

    def add_to_team(self, **kw):
        """
        We override this method to add our additional participation
        policy groups, as detailed in available_groups above
        """
        group = self.context.participant_policy
        data = kw.copy()
        if "groups" in data:
            data["groups"].add(group)
        else:
            data["groups"] = set([group])

        super(PloneIntranetWorkspace, self).add_to_team(**data)


class WorkspaceLocalRoleAdapter(DefaultLocalRoleAdapter):
    """
    If the user has the local role of Owner on the context
    and the acquired role of SelfPublisher; they should also be given Reviewer.

    """
    implements(ILocalRoleProvider)
    adapts(IContentish)

    def getRoles(self, principal_id):
        """
        give an Owner who is also a 'selfpublisher', the reviewer role
        """
        context = self.context
        current_roles = list(DefaultLocalRoleAdapter.getRoles(
            self,
            principal_id,
        ))

        # check we are not on the workspace itself
        if IHasWorkspace.providedBy(context):
            return current_roles
        # otherwise we should acquire the workspace and check out roles
        workspace = getattr(context, 'acquire_workspace', lambda: None)()
        if workspace is None:
            return current_roles

        workspace_roles = api.user.get_roles(obj=workspace)
        if 'SelfPublisher' in workspace_roles and 'Owner' in current_roles:
            current_roles.append('Reviewer')
        return current_roles
