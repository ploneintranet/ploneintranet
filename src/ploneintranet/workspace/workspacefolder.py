from five import grok

from plone.dexterity.content import Container
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable


class IWorkspaceFolder(form.Schema, IImageScaleTraversable):
    """
    A WorkspaceFolder users can collaborate in
    """

    # If you want a schema-defined interface, delete the model.load
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/workspace.xml to define the content type.

    form.model("models/workspacefolder.xml")


class WorkspaceFolder(Container):
    grok.implements(IWorkspaceFolder)

    # Block local role acquisition so that users
    # must be given explicit access to the workspace
    __ac_local_roles_block__ = 1


class SampleView(grok.View):
    """ sample view class """

    grok.context(IWorkspaceFolder)
    grok.require('zope2.View')

    # grok.name('view')
