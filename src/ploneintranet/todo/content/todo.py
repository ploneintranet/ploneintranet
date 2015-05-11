from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implements

from .. import _
from ..behaviors import ITodoMarker


class ITodo(model.Schema):
    """A todo content type
    """

    title = schema.TextLine(title=_("Task"))


class Todo(Item):
    implements(ITodo, ITodoMarker)
