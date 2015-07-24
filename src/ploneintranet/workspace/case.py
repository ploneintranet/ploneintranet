from plone import api
from ploneintranet.attachments.attachments import IAttachmentStoragable
from zope.interface import implementer

from .config import TEMPLATES_FOLDER
from .workspacefolder import IWorkspaceFolder
from .workspacefolder import WorkspaceFolder


class ICase(IWorkspaceFolder):
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


def create_case_from_template(template_id, target_id=None):
    portal = api.portal.get()
    template_folder = portal.restrictedTraverse(TEMPLATES_FOLDER)
    if template_folder:
        src = template_folder.restrictedTraverse(template_id)
        if src:
            target_folder = portal.restrictedTraverse('workspaces')
            new = api.content.copy(
                source=src,
                target=target_folder,
                id=target_id,
                safe_id=True,
            )
            return new
