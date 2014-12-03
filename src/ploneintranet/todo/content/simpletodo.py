from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implements

from ploneintranet.todo import _
from ploneintranet.todo.vocabularies import todo_status, todo_priority


class ISimpleTodo(model.Schema):
    """A simple todo content type
    """

    taskname = schema.TextLine(title=_("Task"))

    assignee = schema.Choice(
        title=_(u"Assignee"),
        description=_("A user (or a group) assigned to this task"),
        required=False,
        vocabulary="plone.principalsource.Principals"
        )

    workspace = schema.TextLine(
        title=_(u"Workspace"),
        description=_(u"The workspace assigned to this task"),
        required=False,
        )

    status = schema.Choice(
        title=_(u"Status"),
        required=True,
        default=u'tbd', 
        vocabulary=todo_status,
        )

    priority = schema.Choice(
        title=_(u"Priority"),
        required=True,
        default=1, 
        vocabulary=todo_priority,
        )


class SimpleTodo(Item):
    implements(ISimpleTodo)