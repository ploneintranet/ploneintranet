from ploneintranet.search.interfaces import ISiteSearch
from Products.CMFPlone.utils import safe_unicode
from zope.component import getUtility
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory
from zope.interface import implements


class IDivisionsVocabularyFactory(IVocabularyFactory):
    """Creates vocabularies that are both context- and request-aware"""

    def __call__(context, request, query=None):
        """
        The context provides a location that the vocabulary can make use of.
        The request provides a user that the vocabulary can personalize for.
        The query provides a filter the user has input so far.
        """


class DivisionsVocabulary(object):

    implements(IDivisionsVocabularyFactory)

    def __call__(self, context, request=None, query=None):
        """ Returns all divisions that are currently available in the index"""
        sitesearch = getUtility(ISiteSearch)
        query = dict(is_division=True)
        results = sitesearch.query(filters=query).results

        items = [
            SimpleTerm(safe_unicode(i['Title']), i['UID'],
                       safe_unicode(i['Description']))
            for i in sorted(results, lambda a, b: a['Title'] < b['Title'])
        ]
        return SimpleVocabulary(items)

DivisionsVocabularyFactory = DivisionsVocabulary()
