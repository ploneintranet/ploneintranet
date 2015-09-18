# -*- coding: utf-8 -*-
from binascii import b2a_qp
from logging import getLogger
from plone import api
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
from unidecode import unidecode
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


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

    # will add new suggestion sources until min_matches is reached, if possible
    min_matches = 5
    # optimize for most relevant tag suggestions
    max_suggest = 9

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

        graph = api.portal.get_tool("ploneintranet_network")
        uuid = IUUID(context)
        userid = api.user.get_current().id
        blacklist = []
        tags = []

        # 1. prioritize "old" context tags
        #    i.e. tags set on context by someone, then removed by someone else
        try:
            # don't bother to sort, it'll only ever be a handful
            tags = self._filter(
                [x for x in graph.get_tags("content", uuid).keys()],
                blacklist, query, True)
            blacklist.extend(tags)  # avoid duplication
        except KeyError:
            # untagged content
            pass

        # 2. personal tag set on content
        if len(tags) < self.min_matches:
            try:
                counted = [(len(ids), tag) for (tag, ids)
                           in graph.get_tagged('content', userid).items()]
            except AttributeError:
                # no personal tags yet
                pass
            else:
                counted.sort()
                counted.reverse()  # most used on top
                # optimize suggestion set for most relevant tags
                counted = counted[:self.max_suggest - len(tags)]
                tags.extend(self._filter([x[1] for x in counted],
                                         blacklist, query, True))
                blacklist.extend(tags)  # avoid duplication

        # 3. personal tag set on microblog
        # not implemented yet because microblog tagging integration
        # into network is TODO FIXME

        # 4. fall back to catalog, list all Subject indexed tags
        if len(tags) < self.min_matches:
            tags.extend(self._filter(self._catalog_subjects(),
                                     blacklist, query, True))

        # finally, turn the tag list into a vocabulary
        tags.sort()
        items = [
            SimpleTerm(i, b2a_qp(safe_encode(i)), safe_unicode(i))
            for i in tags
        ]
        return SimpleVocabulary(items)

    def _catalog_subjects(self, query=None):
        """Fallback to the upstream vocabulary items generation"""
        catalog = api.portal.get_tool("portal_catalog")
        if catalog is None:
            return []
        index = catalog._catalog.getIndex('Subject')
        return [safe_unicode(i) for i in index._index]

    def _filter(self, tags, blacklist, query=None, fuzzy=False):
        """ If fuzzy is set, perform a case-insensitive matching. Also,
        additionally convert non-ascii characters to their ascii representation
        for the matching. That means "Borse" will also find "Börse" and vice
        versa. """
        result = set()
        # `query` can be a string, therefore we must make sure it is unicode
        # before applying unidecode. Note:
        # >>> unidecode(u'ö')
        # 'o'   # Correct
        # >>> unidecode('ö')
        # 'AP'  # Wrong!
        # Or, in different rendering
        # >>> unidecode(u'\xf6')      # corresponds to u'ö'
        # 'o'   # Correct
        # >>> unidecode('\xc3\xb6')   # corresponds to 'ö'
        # 'AP'  # Wrong!
        # >>> unidecode(u'\xc3\xb6')  # corresponds to u'Ã¶' (!)
        # 'AP'  # Also wrong, obviously
        # and then query can also be None, which should not be decoded
        if query:
            q_unidecode = unidecode(safe_unicode(query)).lower()
        else:
            q_unidecode = None
        # Pass the `fuzzy` switch to safe_encode. If set, the term will be
        # converted to lower-case
        query = safe_encode(query, fuzzy)
        for tag in tags:
            if tag in blacklist:
                continue
            if query is None or query in safe_encode(tag, fuzzy):
                result.add(tag)
            # `q_unidecode` might be empty, since not all chars have a letter
            # representation:
            # unidecode(u'♥') == ''
            if fuzzy and q_unidecode and q_unidecode in unidecode(tag).lower():
                result.add(tag)
        return list(result)


def safe_encode(term, fuzzy=False):
    if isinstance(term, unicode):
        # no need to use portal encoding for transitional encoding from
        # unicode to ascii. utf-8 should be fine.
        term = term.encode('utf-8')
    if fuzzy and term is not None:
        return term.lower()
    return term


PersonalizedKeywordsVocabularyFactory = PersonalizedKeywordsVocabulary()
