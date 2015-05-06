from plone.dexterity.content import Container
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable
from ploneintranet.attachments.attachments import IAttachmentStoragable
from zope.interface import implementer


class IWorkspaceContainer(form.Schema, IImageScaleTraversable):
    """
    Marker interface for WorkspaceContainer
    """


@implementer(IWorkspaceContainer, IAttachmentStoragable)
class WorkspaceContainer(Container):
    """
    A folder to contain WorkspaceFolders
    """
