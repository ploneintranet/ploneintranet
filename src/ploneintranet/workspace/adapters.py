from collective.workspace.workspace import Workspace


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
        group = self.context.participant_policy
        data = kw.copy()
        if "groups" in data:
            data["groups"].add(group)
        else:
            data["groups"] = set([group])

        super(PloneIntranetWorkspace, self).add_to_team(**data)
