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
        # First of all we take the set of the todo assignees
        pc = api.portal.get_tool('portal_catalog')
        review_state = api.content.get_state(self)
        brains = pc.unrestrictedSearchResults(
            path='/'.join(self.getPhysicalPath()),
            portal_type='todo',
        )
        objs = filter(
            lambda obj: obj.assignee and obj.milestone == review_state,
            (brain._unrestrictedGetObject() for brain in brains)
        )
        assignees = {obj.assignee for obj in objs}

        # now we make a partition of the user associated to this context
        existing_users = self.existing_users()

        existing_guests = set([])
        non_guests = set([])
        for user in existing_users:
            if user.get('role') == 'Guest':
                existing_guests.add(user['id'])
            else:
                non_guests.add(user['id'])

        # We find out which assignees are guests
        entitled_guests = assignees.difference(non_guests)

        workspace = IWorkspace(self)
        # We have some stale guests that should be removed from this context
        stale_guests = existing_guests.difference(entitled_guests)
        for user_id in stale_guests:
            workspace.remove_from_team(user_id)

        # We have some new guests that should be added to this context
        new_guests = entitled_guests.difference(existing_guests)
        for user_id in new_guests:
            workspace.add_to_team(user_id, groups=['Guests'])
