import unittest
from zope.component import queryUtility

from plone import api
from ploneintranet.microblog.interfaces import IMicroblogTool

from ploneintranet.microblog.testing import\
    PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING


class TestContentStatusUpdate(unittest.TestCase):

    layer = PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_content_status_update(self):
        tool = queryUtility(IMicroblogTool)
        doc = api.content.create(
            container=self.portal,
            type='Document',
            title='My document',
        )

        self.assertEqual(0, len([x for x in tool.values()]))
        api.content.transition(doc, to_state='published')
        found = [x for x in tool.values()]
        self.assertEqual(1, len(found))
        su = found[0]
        self.assertEqual(None, su.microblog_context)
        self.assertEqual(doc, su.content_context)
