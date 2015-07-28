# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from plone.app.layout.navigation.interfaces import INavigationRoot
from logging import getLogger
from plone.app.widgets.interfaces import IFieldPermissionChecker
from types import FunctionType
from zope.component import queryAdapter
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory
import inspect

from plone.app.content.browser.vocabulary import VocabularyView
from plone.app.content.browser.vocabulary import VocabLookupException
from plone.app.content.browser.vocabulary import _parseJSON
from plone.app.content.browser.vocabulary import _permissions as base_perms
from plone.app.content.utils import json_dumps
from plone.app.content.utils import json_loads

from ploneintranet.network.vocabularies import IPersonalizedVocabularyFactory


logger = getLogger(__name__)

_permissions = {
    'ploneintranet.network.vocabularies.Keywords': 'Modify portal content',
}


class PersonalizedVocabularyView(VocabularyView):
    """
    Queries a named personalized vocabulary and returns
    JSON-formatted results.

    Replaces plone.app.content.browser.vocabulary.VocabularyView
    """

    def get_vocabulary(self):
        """
        Look up named vocabulary and check permissions.
        Unline p.a.content.browser.vocabulary.VocabularyView
        this resolves a IPersonalizedVocabularyFactory
        and calls it with both context and request to
        enable personalization.
        """
        # --- only slightly changed from upstream ---

        # Look up named vocabulary and check permission.
        context = self.context
        factory_name = self.request.get('name', None)
        field_name = self.request.get('field', None)
        if not factory_name:
            raise VocabLookupException('No factory provided.')

        if factory_name in base_perms:
            # don't mess with upstream vocabulary handling
            return super(PersonalizedVocabularyView, self).get_vocabulary()

        authorized = None
        sm = getSecurityManager()
        if (factory_name not in _permissions or
                not INavigationRoot.providedBy(context)):
            # Check field specific permission
            if field_name:
                permission_checker = queryAdapter(context,
                                                  IFieldPermissionChecker)
                if permission_checker is not None:
                    authorized = permission_checker.validate(field_name,
                                                             factory_name)
            if not authorized:
                # zope admin misses workspace access, go figure
                logger.error("Vocabulary %s lookup (%s) not allowed",
                             factory_name, field_name)
                raise VocabLookupException('Vocabulary lookup not allowed')
        # Short circuit if we are on the site root and permission is
        # in global registry
        elif not sm.checkPermission(_permissions[factory_name], context):
            raise VocabLookupException('Vocabulary lookup not allowed')

        factory = queryUtility(IVocabularyFactory, factory_name)
        if not factory:
            raise VocabLookupException(
                'No factory with name "%s" exists.' % factory_name)

        # This part is for backwards-compatibility with the first
        # generation of vocabularies created for plone.app.widgets,
        # which take the (unparsed) query as a parameter of the vocab
        # factory rather than as a separate search method.
        if type(factory) is FunctionType:
            factory_spec = inspect.getargspec(factory)
        else:
            factory_spec = inspect.getargspec(factory.__call__)
        query = _parseJSON(self.request.get('query', ''))
        if query and 'query' in factory_spec.args:
            vocabulary = factory(context, query=query)

        # This is what is reached for non-legacy vocabularies.

        elif IPersonalizedVocabularyFactory.providedBy(factory):
            # patternslib select2 queries for "q" instead of "query"
            if not query and self.request.get('q', False):
                query = _parseJSON(self.request.get('q'))
            # this is the key customization: feed in the request
            vocabulary = factory(context, self.request, query=query)
        else:
            # default fallback
            vocabulary = factory(context)

        return vocabulary

    def __call__(self):
        """ If the 'resultsonly' parameter is in the request then extract the
        value for "results" from the JSON string returned from the default
        @@getVocabulary view, so that it can be used by pat-autosuggest.

        @@getVocabulary also uses the vocabulary item 'token' value for the
        'id', which escapes unicode strings. For pat-autosuggest we need to use
        unicode for both the 'text' and the 'id'.
        """
        vocab_json = super(PersonalizedVocabularyView, self).__call__()
        if vocab_json and self.request.get('resultsonly', False):
            vocab_obj = json_loads(vocab_json)
            results = vocab_obj.get('results', [])
            text_values = [i['text'] for i in results]
            vocab_list = [{'text': val, 'id': val} for val in text_values]
            return json_dumps(vocab_list)

        return vocab_json
