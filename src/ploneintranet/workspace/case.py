from ploneintranet.attachments.attachments import IAttachmentStoragable
from zope.interface import implementer

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
