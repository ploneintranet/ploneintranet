from plone import api
from ploneintranet.simplesharing.tests.base import BaseTestCase
from ploneintranet.simplesharing.vocabularies import WorkflowStatesSource
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm


class TestWorkflowStatesSource(BaseTestCase):

    def test_class(self):
        """
        test the vocab's __call__ method
        """
        self.login_as_portal_owner()
        doc = api.content.create(
            container=self.portal,
            type='Document',
            id='my-doc',
        )
        cls = WorkflowStatesSource()
        vocab = cls.__call__(doc)

        self.assertIsInstance(vocab, SimpleVocabulary)
        self.assertEqual(len(vocab), 1)
        self.assertIsInstance(list(vocab)[0], SimpleTerm)
        self.assertIn('Visible to everyone', list(vocab)[0].title)
