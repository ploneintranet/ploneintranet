from plone.directives import form
from zope.interface import alsoProvides, Interface
from zope.schema import Bool, Choice, Date, TextLine, Text

from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from .vocabularies import todo_priority


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

    description = Text(
        title=u"Long description",
        required=False
    )

    initiator = TextLine(
        title=_(u"Initiator"),
        description=_("The user (or group) who requested this task"),
        required=False,
    )

    assignee = TextLine(
        title=_(u"Assignee"),
        description=_("A user (or a group) assigned to this task"),
        required=False,
    )

    priority = Choice(
        title=_(u"Priority"),
        required=True,
        default=1,
        vocabulary=todo_priority,
    )

    due = Date(title=_(u"Due date"), required=False)

alsoProvides(ITodo, form.IFormFieldProvider)


class ITodoMarker(Interface):
    """Marker interface that will be provided by instances using the
    ITodo behavior.
    """


class IMilestone(form.Schema):
    """A text field representing the milestone associated with this todo item.
    For example, the id of the associated workflow state of the container.
    """
    milestone = TextLine(
        title=_(u"Milestone"),
        required=False,
    )

alsoProvides(IMilestone, form.IFormFieldProvider)


class IMilestoneMarker(Interface):
    """Marker interface that will be provided by instances using the
    IMilestone behavior.
    """
