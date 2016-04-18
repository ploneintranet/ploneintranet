# coding=utf-8
from Products.CMFPlone.utils import safe_unicode
from plone import api
from ploneintranet.workspace.workspacefolder import IWorkspaceFolder
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


class DivisionSimpleTerm(SimpleTerm):
    ''' This is like a simpleterm but carries a description as a metadata
    '''
    def __init__(self, value, token=None, title=None, description=u''):
        """ Adds the description optional parameter to the simple term
        """
        super(DivisionSimpleTerm, self).__init__(value, token, title)
        self.description = description


class DivisionsVocabulary(object):

    implements(IDivisionsVocabularyFactory)

    def __call__(self, context, request=None, query=None):
        """ Returns all divisions that are currently available in the index"""
        results = api.content.find(
            is_division=True,
            object_provides=IWorkspaceFolder,
        )
        items = [
            DivisionSimpleTerm(
                item.UID,
                title=safe_unicode(item.Title),
                description=safe_unicode(item.Description),
            )
            for item in sorted(
                results,
                key=lambda x: safe_unicode(x.Title)
            )
        ]
        return SimpleVocabulary(items)

DivisionsVocabularyFactory = DivisionsVocabulary()
