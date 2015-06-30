# -*- coding: utf-8 -*-
from ploneintranet.network.graph import NetworkGraph
from ploneintranet.network.interfaces import INetworkGraph
from ploneintranet.network.testing import IntegrationTestCase
from zope.interface.verify import verifyClass
from BTrees import OOBTree


class TestTags(IntegrationTestCase):

    def test_verify_interface(self):
        self.assertTrue(verifyClass(INetworkGraph, NetworkGraph))

    def test_unpack_treeset(self):
        struct = OOBTree.OOTreeSet()
        struct.insert('foo')
        struct.insert('bar')
        g = NetworkGraph()
        flat = g.unpack(struct)
        self.assertEqual(flat, ['bar', 'foo'])

    def test_unpack_btree_treeset(self):
        struct = OOBTree.OOBTree()
        struct['foo'] = OOBTree.OOTreeSet()
        struct['foo'].insert('baz')
        struct['foo'].insert('bar')
        g = NetworkGraph()
        flat = g.unpack(struct)
        self.assertEqual(flat, {'foo': ['bar', 'baz']})

    def test_unpack_nested_btree_treeset(self):
        struct = OOBTree.OOBTree()
        struct['foo'] = OOBTree.OOBTree()
        struct['foo']['fooz'] = OOBTree.OOTreeSet()
        struct['foo']['fooz'].insert('baz')
        struct['foo']['fooz'].insert('bar')
        g = NetworkGraph()
        flat = g.unpack(struct)
        self.assertEqual(flat, {'foo': {'fooz': ['bar', 'baz']}})

    def test_user_tag(self):
        g = NetworkGraph()
        # alex tags bernard with 'leadership'
        g.tag('user', 'bernard', 'alex', 'leadership')
        self.assertEqual(['leadership'],
                         list(g.get_tags('user', 'bernard', 'alex')))

    def test_user_tag_utf8(self):
        g = NetworkGraph()
        # alex tags bernard with 'leadership'
        g.tag('user', u'bernard ♥', u'alex ☀', u'leadership ☃')
        self.assertEqual([u'leadership ☃'],
                         list(g.get_tags('user', u'bernard ♥', u'alex ☀')))

    def test_utf8_args(self):
        """BTree keys MUST be of type unicode. Check that the implementation
        enforces this."""
        g = NetworkGraph()
        self.assertRaises(AttributeError, g.tag, 'user', 1, '2', '3')
        self.assertRaises(AttributeError, g.tag, 'user', '1', 2, '3')
        self.assertRaises(AttributeError, g.tag, 'user', '1', '2', 3)
        self.assertRaises(AttributeError, g.untag, 'user', 1, '2', '3')
        self.assertRaises(AttributeError, g.untag, 'user', '1', 2, '3')
        self.assertRaises(AttributeError, g.untag, 'user', '1', '2', 3)

    def test_user_tag_multi(self):
        g = NetworkGraph()
        # alex tags bernard with 'leadership' and 'change management'
        g.tag('user', 'bernard', 'alex', 'leadership', 'change management')
        self.assertEqual(['change management', 'leadership'],
                         sorted(list(g.get_tags('user', 'bernard', 'alex'))))

    def test_user_tag_untag(self):
        g = NetworkGraph()
        g.tag('user', 'bernard', 'alex', 'leadership', 'change management')
        g.untag('user', 'bernard', 'alex', 'leadership')
        self.assertEqual(['change management'],
                         list(g.get_tags('user', 'bernard', 'alex')))

    def test_get_tagged_all(self):
        g = NetworkGraph()
        g.tag('user', 'bernard', 'alex', 'leadership', 'change management')
        g.tag('user', 'caroline', 'alex', 'leadership', 'negotiations')
        g.tag('content', 'doc1', 'alex', 'negotiations')
        tagged = sorted(list(g.get_tagged('user', 'alex', 'leadership')))
        self.assertEqual(tagged, ['bernard', 'caroline'])
        tagged = sorted(list(g.get_tagged('content', 'alex', 'negotiations')))
        self.assertEqual(tagged, ['doc1'])

    def test_get_tagged_nomatch(self):
        g = NetworkGraph()
        g.tag('user', 'bernard', 'alex', 'leadership', 'change management')
        g.tag('user', 'caroline', 'alex', 'leadership', 'negotiations')
        g.tag('content', 'doc1', 'alex', 'negotiations')
        tagged = sorted(list(g.get_tagged('user', 'bernard', 'leadership')))
        self.assertEqual(tagged, [])

    def test_get_tagged_noitemtype(self):
        g = NetworkGraph()
        g.tag('user', 'bernard', 'alex', 'leadership', 'change management')
        g.tag('user', 'caroline', 'alex', 'leadership', 'negotiations')
        g.tag('content', 'doc1', 'alex', 'negotiations')
        tagged = g.get_tagged(None, 'alex', 'leadership')
        self.assertEqual(
            tagged, {'content': [],
                     'user': ['bernard', 'caroline']}
        )

    def test_get_tagged_nouserid(self):
        g = NetworkGraph()
        g.tag('user', 'bernard', 'alex', 'leadership', 'change management')
        g.tag('user', 'caroline', 'alex', 'leadership', 'negotiations')
        g.tag('content', 'doc1', 'alex', 'negotiations')
        tagged = g.get_tagged('user', None, 'leadership')
        self.assertEqual(
            tagged, {'bernard': ['alex'], 'caroline': ['alex']}
        )

    def test_get_tagged_notag(self):
        g = NetworkGraph()
        g.tag('user', 'bernard', 'alex', 'leadership', 'change management')
        g.tag('user', 'caroline', 'alex', 'leadership', 'negotiations')
        g.tag('content', 'doc1', 'alex', 'negotiations')
        tagged = g.get_tagged('user', 'alex', None)
        self.assertEqual(
            tagged, {'change management': ['bernard'],
                     'leadership': ['bernard', 'caroline'],
                     'negotiations': ['caroline']}
        )

    def test_get_tagged_only_item_type(self):
        g = NetworkGraph()
        g.tag('user', 'bernard', 'alex', 'leadership', 'change management')
        g.tag('user', 'caroline', 'alex', 'leadership', 'negotiations')
        g.tag('content', 'doc1', 'alex', 'negotiations')
        tagged = g.get_tagged('user', None, None)
        self.assertEqual(
            tagged, {'bernard': {'change management': ['alex'],
                                 'leadership': ['alex']},
                     'caroline': {'leadership': ['alex'],
                                  'negotiations': ['alex']}}
        )

    def test_get_tagged_only_user_id(self):
        g = NetworkGraph()
        g.tag('user', 'bernard', 'alex', 'leadership', 'change management')
        g.tag('user', 'caroline', 'alex', 'leadership', 'negotiations')
        g.tag('content', 'doc1', 'alex', 'negotiations')
        tagged = g.get_tagged(None, 'alex', None)
        self.assertEqual(
            tagged, {'change management': {'content': [],
                                           'user': ['bernard']},
                     'leadership': {'content': [],
                                    'user': ['bernard', 'caroline']},
                     'negotiations': {'content': ['doc1'],
                                      'user': ['caroline']}}
        )

    def test_get_tagged_only_tag(self):
        g = NetworkGraph()
        g.tag('user', 'bernard', 'alex', 'leadership', 'change management')
        g.tag('user', 'caroline', 'alex', 'leadership', 'negotiations')
        g.tag('content', 'doc1', 'alex', 'negotiations')
        tagged = g.get_tagged(None, None, 'negotiations')
        self.assertEqual(
            tagged, {'content': {'doc1': ['alex']},
                     'user': {'caroline': ['alex']}}
        )

    def test_get_tagged_noparams(self):
        g = NetworkGraph()
        g.tag('user', 'bernard', 'alex', 'leadership', 'change management')
        g.tag('user', 'caroline', 'alex', 'leadership', 'negotiations')
        g.tag('content', 'doc1', 'alex', 'negotiations')
        tagged = g.get_tagged()
        self.assertEqual(
            tagged, {'alex': {'change management': {'content': [],
                                                    'user': ['bernard']},
                              'leadership': {'content': [],
                                             'user': ['bernard', 'caroline']},
                              'negotiations': {'content': ['doc1'],
                                               'user': ['caroline']}}}
        )

    def test_get_taggers(self):
        g = NetworkGraph()
        g.tag('user', 'bernard', 'alex', 'leadership', 'change management')
        g.tag('user', 'caroline', 'alex', 'leadership', 'negotiations')
        g.tag('content', 'doc1', 'alex', 'negotiations')
        # an extra tag here
        g.tag('user', 'bernard', 'caroline', 'negotiations')
        taggers = g.unpack(g.get_taggers('user', 'bernard', 'leadership'))
        self.assertEqual(taggers, ['alex'])

    def test_get_taggers_notag(self):
        g = NetworkGraph()
        g.tag('user', 'bernard', 'alex', 'leadership', 'change management')
        g.tag('user', 'caroline', 'alex', 'leadership', 'negotiations')
        g.tag('content', 'doc1', 'alex', 'negotiations')
        # an extra tag here
        g.tag('user', 'bernard', 'caroline', 'negotiations')
        taggers = g.unpack(g.get_taggers('user', 'bernard'))
        self.assertEqual(taggers,
                         {'change management': ['alex'],
                          'leadership': ['alex'],
                          'negotiations': ['caroline']})

    def test_get_tags(self):
        g = NetworkGraph()
        g.tag('user', 'bernard', 'alex', 'leadership', 'change management')
        g.tag('content', 'doc1', 'caroline', 'leadership', 'negotiations')
        g.tag('content', 'doc1', 'alex', 'negotiations')
        tags = g.unpack(g.get_tags('content', 'doc1', 'caroline'))
        self.assertEqual(tags, ['leadership', 'negotiations'])

    def test_get_tags_nouser(self):
        g = NetworkGraph()
        g.tag('user', 'bernard', 'alex', 'leadership', 'change management')
        g.tag('content', 'doc1', 'caroline', 'leadership', 'negotiations')
        g.tag('content', 'doc1', 'alex', 'negotiations')
        tags = g.unpack(g.get_tags('content', 'doc1',))
        self.assertEqual(tags, {'negotiations': ['alex', 'caroline'],
                                'leadership': ['caroline']})

    def test_is_tagged(self):
        g = NetworkGraph()
        g.tag('user', 'bernard', 'alex', 'leadership', 'change management')
        self.assertTrue(
            g.is_tagged('user', 'bernard', 'alex', 'change management'))
        self.assertFalse(
            g.is_tagged('user', 'bernard', 'alex', 'negotiation'))
        self.assertFalse(
            g.is_tagged('content', 'doc1', 'alex', 'leadership'))
