from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


WORKFLOW_MAPPING = {
    'private': 'draft',
    'limited': 'draft',
    'published': 'published',
    'public': 'public'
}


def workflow_states_vocab(context):
    return SimpleVocabulary([
        SimpleTerm(u'private', u'private', u'Only visible to me'),
        SimpleTerm(u'limited', u'limited', u'Share with selected users'),
        SimpleTerm(u'published', u'published', u'Shared with my team'),
        SimpleTerm(u'public', u'public', u'Shared with all Intranet users')
    ])
