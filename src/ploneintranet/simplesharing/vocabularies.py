from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


def workflow_states_vocab(context):
    SimpleVocabulary([
        SimpleTerm(u'thingy'),
        SimpleTerm(u'mabob'),
    ])
