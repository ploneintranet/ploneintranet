from binascii import b2a_qp
from logging import getLogger
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.site.hooks import getSite

logger = getLogger(__name__)


class IPersonalizedVocabularyFactory(IVocabularyFactory):
    """Creates vocabularies that are both context- and request-aware"""

    def __call__(context, request, query=None):
        """
        The context provides a location that the vocabulary can make use of.
        The request provides a user that the vocabulary can personalize for.
        The query provides a filter the user has input so far.
        """


class PersonalizedKeywordsVocabulary(object):
    """
    Vocabulary factory listing personalized keywords based on the
    ploneintranet.network personalized tag store.

    Replaces plone.app.vocabularies.catalog.KeywordsVocabulary.
    """

    implements(IPersonalizedVocabularyFactory)

    def __call__(self, context, request=None, query=None):
        """
        We take advantage of the fact that this method is called
        for *every keystroke* in the subjects widget, so we can
        adjust the tag suggestions based on the number of matching
        tag suggestion candidates we're finding based on the query,
        which is the substring the user has input so far.
        """
        # get network graph
        # list tags for (context, user), filtered for query
        # prioritzed by count
        # if no matching: fall back to global tag set
        # return vocabulary

        logger.info(".__call__(%s, %s, %s)",
                    repr(context), repr(request), query)

        # --- upstream ---
        site = getSite()
        self.catalog = getToolByName(site, "portal_catalog", None)
        if self.catalog is None:
            return SimpleVocabulary([])
        index = self.catalog._catalog.getIndex('Subject')

        def safe_encode(term):
            if isinstance(term, unicode):
                # no need to use portal encoding for transitional encoding from
                # unicode to ascii. utf-8 should be fine.
                term = term.encode('utf-8')
            return term

        # Vocabulary term tokens *must* be 7 bit values, titles *must* be
        # unicode
        items = [
            SimpleTerm(i, b2a_qp(safe_encode(i)), safe_unicode(i))
            for i in index._index
            if query is None or safe_encode(query) in safe_encode(i)
        ]
        return SimpleVocabulary(items)


PersonalizedKeywordsVocabularyFactory = PersonalizedKeywordsVocabulary()
