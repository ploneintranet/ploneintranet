from plone.dexterity.content import Container
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable
from ploneintranet.attachments.attachments import IAttachmentStoragable
from ploneintranet.layout.interfaces import IAppContainer
from ploneintranet.layout.app import AbstractAppContainer
from zope.interface import implementer

from ploneintranet.workspace.interfaces import IWorkspaceAppContentLayer
from ploneintranet.workspace.interfaces import IWorkspaceAppFormLayer


class IWorkspaceContainer(form.Schema,
                          IImageScaleTraversable,
                          IAppContainer):
    """
    Marker interface for WorkspaceContainer
    """


@implementer(IWorkspaceContainer, IAttachmentStoragable, IAppContainer)
class WorkspaceContainer(AbstractAppContainer, Container):
    """
    A folder to contain WorkspaceFolders.

    Implements IAppContainer to enable workspace-specific content view
    registrations.
    """

    app_name = "workspace"  # should not contain dots
    app_layers = (IWorkspaceAppContentLayer, IWorkspaceAppFormLayer)
