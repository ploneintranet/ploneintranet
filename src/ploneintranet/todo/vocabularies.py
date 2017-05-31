from ploneintranet.core import ploneintranetCoreMessageFactory as _
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


todo_priority = SimpleVocabulary(
    [
        SimpleTerm(value=-1, title=_(u'No priority')),
        SimpleTerm(value=0, title=_(u'Low')),
        SimpleTerm(value=1, title=_(u'Medium')),
        SimpleTerm(value=2, title=_(u'High'))
    ]
)
