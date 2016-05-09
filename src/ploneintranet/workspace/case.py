# coding=utf-8
from collective.workspace.interfaces import IWorkspace
from plone import api
from ploneintranet.attachments.attachments import IAttachmentStoragable
from ploneintranet.workspace.interfaces import IBaseWorkspaceFolder
from ploneintranet.workspace.workspacefolder import WorkspaceFolder
from zope.interface import implementer


class ICase(IBaseWorkspaceFolder):
    """
    Interface for Case
    """


@implementer(ICase, IAttachmentStoragable)
class Case(WorkspaceFolder):
    """
    A Case users can collaborate on
    """

    @property
    def is_case(self):
        """ XXX remove after case refactoring """
        return True

    @property
    def ws_type(self):
        """
        returns a string for use in a css selector in the templates
        describing this content type
        Override in custom workspace types
        """
        return "case"

    def update_case_access(self):
        """
        Iterate over all tasks inside the case.
        - If a member is assigned to a task and the task in the current
          milestone:
          Grant Guest access, if the user is not a regular member of the Case
        - If a member has Guest access, but is not an assignee in any
          task of the current milestone:
          Remove Guest access
        """
        wft = api.portal.get_tool("portal_workflow")
        case_state = wft.getInfoFor(self, "review_state")

        tasks_by_state = self.tasks()
        existing_users = self.existing_users_by_id()

        remove_access = set()
        grant_access = set()
        for state in tasks_by_state:
            for task in tasks_by_state[state]:
                if not task.get('assignee'):
                    continue
                assignee_id = task.get('assignee').getId()
                if case_state == state:
                    if (
                        assignee_id not in existing_users or
                        (assignee_id in existing_users and
                            existing_users[assignee_id]['role'] == 'Guest')
                    ):
                        grant_access.add(assignee_id)
                else:
                    if (
                        assignee_id in existing_users and
                        existing_users[assignee_id]['role'] == 'Guest'
                    ):
                        remove_access.add(assignee_id)
        workspace = IWorkspace(self)
        # We don't need to remove users that will be added again
        remove_ids = [id for id in remove_access if id not in grant_access]
        # We don't need to grant access to users who already have it
        grant_ids = [id for id in grant_access if id not in remove_access]
        for user_id in remove_ids:
            workspace.remove_from_team(user_id)
        for user_id in grant_ids:
            workspace.add_to_team(user_id, groups=['Guests'])
