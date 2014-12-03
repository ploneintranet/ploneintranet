from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implements

from ploneintranet.todo import _


class ISimpleTodo(model.Schema):
    """A simple todo content type
    """

    taskname = schema.TextLine(title=_("Task"))


class SimpleTodo(Item):
    implements(ISimpleTodo)