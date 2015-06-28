# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.uuid.interfaces import IUUID
from zope.component import getUtility

from ploneintranet.network.interfaces import INetworkTool
from ploneintranet.network.behaviors.metadata import IDublinCore
from ploneintranet.network.testing import IntegrationTestCase


class TestMetadata(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.graph = getUtility(INetworkTool)
        api.user.create(username='john_doe', email='john@doe.org')
        setRoles(self.portal, 'john_doe', ['Manager', ])
        api.user.create(username='mary_jane', email='mary@jane.org')
        setRoles(self.portal, 'mary_jane', ['Manager', ])

        # profiles:default already replaces upstream dublincore with our fork

    def test_subject_set_get(self):
        self.login('john_doe')
        doc1 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc1',
            title='Doc 1',
        )
        wrapped = IDublinCore(doc1)
        wrapped.subjects = ('foo', 'bar')
        # adapter.subjects - obj.subject
        # ---------------^   -----------!
        self.assertEqual(doc1.subject, ('foo', 'bar'))

    def test_subject_tags(self):
        self.login('john_doe')
        doc1 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc1',
            title='Doc 1',
        )
        uuid = IUUID(doc1)
        wrapped = IDublinCore(doc1)
        wrapped.subjects = ('foo', 'bar')
        tags = self.graph.get_tags('content', uuid, 'john_doe')
        self.assertEqual(sorted(tags), ['bar', 'foo'])

    def test_subject_tags_utf8(self):
        self.login('john_doe')
        doc1 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc1',
            title='Doc 1',
        )
        uuid = IUUID(doc1)
        wrapped = IDublinCore(doc1)
        wrapped.subjects = (u'foo', u'gemäß-☃')
        tags = self.graph.get_tags('content', uuid, 'john_doe')
        self.assertEqual(sorted(tags), [u'foo', u'gemäß-☃'])

    def test_subject_tags_unset(self):
        self.login('john_doe')
        doc1 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc1',
            title='Doc 1',
        )
        uuid = IUUID(doc1)
        wrapped = IDublinCore(doc1)
        wrapped.subjects = ('foo', 'bar')
        wrapped.subjects = ()
        tags = self.graph.get_tags('content', uuid, 'john_doe')
        self.assertEqual(sorted(tags), [])
        self.assertEqual(doc1.subject, ())

    def test_subject_tags_set_empty(self):
        self.login('john_doe')
        doc1 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc1',
            title='Doc 1',
        )
        wrapped = IDublinCore(doc1)
        # the check is that this doesn't raise a KeyError
        wrapped.subjects = ()

    def test_subject_untags(self):
        self.login('john_doe')
        doc1 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc1',
            title='Doc 1',
        )
        uuid = IUUID(doc1)
        wrapped = IDublinCore(doc1)
        wrapped.subjects = ('foo', 'bar')
        wrapped.subjects = ('foo', 'beer')
        tags = self.graph.get_tags('content', uuid, 'john_doe')
        self.assertEqual(sorted(tags), ['beer', 'foo'])

    def test_subject_multiuser(self):
        self.login('john_doe')
        doc1 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc1',
            title='Doc 1',
        )
        uuid = IUUID(doc1)
        wrapped = IDublinCore(doc1)
        wrapped.subjects = ('foo', 'bar')
        self.login('mary_jane')
        wrapped.subjects = ('foo', 'beer')
        g = self.graph
        self.assertEqual(g.unpack(g.get_taggers('content', uuid, 'beer')),
                         ['mary_jane'])
        self.assertEqual(g.unpack(g.get_taggers('content', uuid, 'bar')),
                         ['john_doe'])
        self.assertEqual(g.unpack(g.get_taggers('content', uuid, 'foo')),
                         ['john_doe', 'mary_jane'])
