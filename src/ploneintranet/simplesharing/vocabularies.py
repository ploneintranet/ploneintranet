from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


def workflow_states_vocab(context):
    return SimpleVocabulary([
        SimpleTerm(u'thingy'),
        SimpleTerm(u'mabob'),
    ])
