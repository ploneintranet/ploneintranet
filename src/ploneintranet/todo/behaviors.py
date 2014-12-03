from plone.directives import form
from zope.interface import alsoProvides, Interface
from zope.schema import Bool, Choice, TextLine

from . import _
from .vocabularies import todo_status, todo_priority


class IMustRead(form.Schema):
    """MustRead schema
    """

    form.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=('mustread',),
    )

    mustread = Bool(
        title=_(u"Must read"),
        description=_(u"""Mark the content as "Must read" for all users."""),
        default=False,
        required=False,
    )

alsoProvides(IMustRead, form.IFormFieldProvider)


class IMustReadMarker(Interface):
    """Marker interface that will be provided by instances using the
    IMustRead behavior.
    """


class ITodo(form.Schema):
    """Todo schema
    """

    assignee = Choice(
        title=_(u"Assignee"),
        description=_("A user (or a group) assigned to this task"),
        required=False,
        vocabulary="plone.principalsource.Principals"
        )

    workspace = TextLine(
        title=_(u"Workspace"),
        description=_(u"The workspace assigned to this task"),
        required=False,
        )

    status = Choice(
        title=_(u"Status"),
        required=True,
        default=u'tbd', 
        vocabulary=todo_status,
        )

    priority = Choice(
        title=_(u"Priority"),
        required=True,
        default=1, 
        vocabulary=todo_priority,
        )

alsoProvides(ITodo, form.IFormFieldProvider)


class ITodoMarker(Interface):
    """Marker interface that will be provided by instances using the
    ITodo behavior.
    """
