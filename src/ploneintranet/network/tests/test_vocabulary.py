# -*- coding: utf-8 -*-
import json
from plone import api
from ploneintranet.network.browser.vocabulary import PersonalizedVocabularyView
from plone.app.testing import setRoles, login

from ploneintranet.network.behaviors.metadata import IDublinCore
from ploneintranet.network.testing import IntegrationTestCase
from ploneintranet.network.vocabularies import PersonalizedKeywordsVocabulary


max_suggest = PersonalizedKeywordsVocabulary.max_suggest
vocab = 'ploneintranet.network.vocabularies.Keywords'


class TestPersonalizedVocabulary(IntegrationTestCase):
    """
    Test both the PersonalizedVocabularyView and via the view
    also the PersonalizedKeywordsVocabulary
    """

    def setUp(self):
        self.portal = self.layer['portal']
        self.catalog = api.portal.get_tool('portal_catalog')
        self.request = self.layer['request']
        self.request.form.update({'name': vocab,
                                  'field': 'subjects'})

        api.user.create(username='john_doe', email='john@doe.org')
        setRoles(self.portal, 'john_doe', ['Manager', ])
        api.user.create(username='mary_jane', email='mary@jane.org')
        setRoles(self.portal, 'mary_jane', ['Manager', ])

        login(self.portal, 'john_doe')

        self.doc1 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc1',
            title='Doc 1'
        )
        few = [u'a_%d_♥' % i for i in xrange(5)]
        few.extend([u'B_%d_☀' % i for i in xrange(5)])
        few.extend([u'RødgrØd', u'rOdgrod'])
        self.num_tags = len(few)
        self.tag(self.doc1, *few)

        self.doc2 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc2',
            title='Doc 2'
        )

        # setUp leaves us logged in as john_doe

    def tag(self, obj, *subjects):
        IDublinCore(obj).subjects = subjects
        obj.reindexObject()
        # reindexObject is not enough to update index._index
        self.catalog.reindexIndex('Subject', None)

    def testVocabularyNoQuery(self):
        """Test the keyword vocab without query narrowing."""
        view = PersonalizedVocabularyView(self.doc2, self.request)
        data = json.loads(view())
        self.assertEquals(len(data['results']), max_suggest)

    def testVocabularySorted(self):
        login(self.portal, 'mary_jane')
        self.tag(self.doc1, 'Z tag')
        self.tag(self.doc1, 'A tag')
        self.tag(self.doc1, 'C tag')
        view = PersonalizedVocabularyView(self.doc2, self.request)
        data = json.loads(view())
        tags = [x['text'] for x in data['results']]
        self.assertEquals(tags[0], u'A tag')
        self.assertEquals(tags[1], u'C tag')
        self.assertEquals(tags[2], u'Z tag')

    def testVocabularyQueryString(self):
        """Test querying a class based vocabulary with a search string.
        """
        self.tag(self.doc1, 'simple')
        view = PersonalizedVocabularyView(self.doc2, self.request)
        self.request.form.update({
            'query': 'simple'
        })
        data = json.loads(view())
        self.assertEquals(len(data['results']), 1)

    def testVocabularyQueryString_utf8(self):
        """Test querying a class based vocabulary with a search string.
        """
        view = PersonalizedVocabularyView(self.doc2, self.request)
        self.request.form.update({
            'query': u'a_3_♥'
        })
        data = json.loads(view())
        self.assertEquals(len(data['results']), 1)

    def testVocabularyQueryStringPartial(self):
        """Test querying a class based vocabulary with a search string.
        """
        view = PersonalizedVocabularyView(self.doc2, self.request)
        self.request.form.update({
            'query': 'a_'  # matches a_?_♥
        })
        data = json.loads(view())
        self.assertEquals(len(data['results']), 5)

    def testVocabularyQueryStringPartial_utf8(self):
        """Test querying a class based vocabulary with a search string.
        """
        view = PersonalizedVocabularyView(self.doc2, self.request)
        self.request.form.update({
            'query': u'♥'  # matches a_?_♥
        })
        data = json.loads(view())
        self.assertEquals(len(data['results']), 5)

    def testVocabularyQueryStringCaseInsensitive(self):
        """Test querying a class based vocabulary with a search string.
        """
        view = PersonalizedVocabularyView(self.doc2, self.request)
        self.request.form.update({
            'query': 'A_'  # matches a_?_♥
        })
        data = json.loads(view())
        self.assertEquals(len(data['results']), 5)
        self.request.form.update({
            'query': 'b_'  # matches B_?_☀
        })
        data = json.loads(view())
        self.assertEquals(len(data['results']), 5)

    def testVocabularyQueryStringUnidecode(self):
        """Test querying a class based vocabulary with a search string.
        """
        view = PersonalizedVocabularyView(self.doc2, self.request)
        self.request.form.update({
            'query': 'rod'  # matches RødgrØd and rOdgrod
        })
        data = json.loads(view())
        self.assertEquals(len(data['results']), 2)

    def testVocabularyQueryStringUnidecodeQuery(self):
        """Test querying a class based vocabulary with a search string.
        """
        view = PersonalizedVocabularyView(self.doc2, self.request)
        self.request.form.update({
            'query': u'RÖD'  # matches RødgrØd and rOdgrod
        })
        data = json.loads(view())
        self.assertEquals(len(data['results']), 2)

    def testVocabularyNoResults(self):
        """Tests that the widgets displays correctly
        """
        view = PersonalizedVocabularyView(self.doc2, self.request)
        self.request.form.update({
            'query': 'nosuch'
        })
        data = json.loads(view())
        self.assertEquals(len(data['results']), 0)

    def testVocabularyUnauthorized(self):
        setRoles(self.portal, 'john_doe', [])
        view = PersonalizedVocabularyView(self.portal, self.request)
        data = json.loads(view())
        self.assertEquals(data['error'], 'Vocabulary lookup not allowed')

    def testVocabularyMissing(self):
        view = PersonalizedVocabularyView(self.portal, self.request)
        self.request.form.update({
            'name': 'vocabulary.that.does.not.exist',
        })
        data = json.loads(view())
        self.assertEquals(data['error'], 'Vocabulary lookup not allowed')

    def testVocabularyNoPersonalTagsYet(self):
        # user has no tags
        login(self.portal, 'mary_jane')
        # doc2 has no tags
        view = PersonalizedVocabularyView(self.doc2, self.request)
        data = json.loads(view())
        # expect john_doe tags on doc1
        self.assertEquals(len(data['results']), self.num_tags)

    def testVocabularyPersonalizedContextTags(self):
        # let john_doe pollute the global tag space via doc2
        self.tag(self.doc2, *['many_%02d' % i for i in xrange(100)])
        login(self.portal, 'mary_jane')
        view = PersonalizedVocabularyView(self.doc1, self.request)
        data = json.loads(view())
        # we expect to find the a_ and b_ doc1 tags only
        self.assertEquals(len(data['results']), self.num_tags)
        self.assertFalse('a_' in data['results'])

    def testVocabularyPersonalizedContextTagsMany(self):
        # let john_doe fill up the doc1 tag space
        self.tag(self.doc1, *['many_%02d' % i for i in xrange(100)])
        login(self.portal, 'mary_jane')
        view = PersonalizedVocabularyView(self.doc1, self.request)
        data = json.loads(view())
        # we expect to find all of john_doe's context tags
        self.assertEquals(len(data['results']), self.num_tags + 100)
        self.assertFalse('a_' in data['results'])

    def testVocabularyPersonalizedUserContentTags(self):
        # mary sets many tags
        login(self.portal, 'mary_jane')
        doc3 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc3',
            title='Doc 3'
        )
        self.tag(doc3, *['many_%02d' % i for i in xrange(100)])
        # john doesn't see those
        login(self.portal, 'john_doe')
        view = PersonalizedVocabularyView(self.doc2, self.request)
        data = json.loads(view())
        # we expect to find john_doe a_* and b_* suggestions only
        self.assertEquals(len(data['results']), max_suggest)
        self.assertFalse('many_' in data['results'])
