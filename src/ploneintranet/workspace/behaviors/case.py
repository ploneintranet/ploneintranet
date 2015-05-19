from plone.autoform.interfaces import IFormFieldProvider
from zope import schema
from zope.interface import alsoProvides
from ploneintranet.workspace.workspacefolder import IWorkspaceFolder

# Implementing this according to
# http://docs.plone.org/external/plone.app.dexterity/docs/behaviors/schema-only-behaviors.html
# to be able to access the attributes directly on the object.


class ICaseMetadata(IWorkspaceFolder):
    """
    Example behavior to extend the workspace
    Intended to be overridden by integrator's code
    """

    case_type = schema.TextLine(
        title=u"Case Type",
        description=u"Type of business case.",
        required=False
    )

alsoProvides(ICaseMetadata, IFormFieldProvider)
