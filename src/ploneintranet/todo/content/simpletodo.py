from plone.dexterity.content import Item
from zope import schema
from zope.interface import implements, Interface

from ploneintranet.todo import _


class ISimpleTodo(Interface):
    """A simple todo content type
    """

    title = schema.TextLine(title=_("Task"))

    assignee = schema.Choice(
        title=_(u"Assignee"),
        description=_("A user (or a group) assigned to this task"),
        vocabulary="plone.principalsource.Principals"
        )


class SimpleTodo(Item):
    implements(ISimpleTodo)