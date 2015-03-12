from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implements

from .. import _
from ..behaviors import ITodoMarker


class ISimpleTodo(model.Schema):
    """A simple todo content type
    """

    title = schema.TextLine(title=_("Task"))


class SimpleTodo(Item):
    implements(ISimpleTodo, ITodoMarker)