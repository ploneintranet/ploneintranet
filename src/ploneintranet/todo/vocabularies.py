from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from ploneintranet.todo import _


todo_priority = SimpleVocabulary(
    [SimpleTerm(value=0, title=_(u'Low')),
     SimpleTerm(value=1, title=_(u'Normal')),
     SimpleTerm(value=2, title=_(u'High'))]
)
