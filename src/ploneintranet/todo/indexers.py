from plone.dexterity.content import CEILING_DATE
from plone.dexterity.utils import datify
from plone.indexer import indexer
from ploneintranet.todo.content.todo import ITodoMarker


@indexer(ITodoMarker)
def due(obj):
    date = getattr(obj, 'due', None)
    date = datify(date)
    return date is None and CEILING_DATE or date
