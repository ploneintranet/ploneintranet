# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.news.testing import FunctionalTestCase
import lxml


class MagazineTest(FunctionalTestCase):
    '''
    Because sqlalchemy gives threading errors when hit via ZServer,
    we fake browser interactions directly on the testing thread itself.
    '''

    def setUp(self):
        super(MagazineTest, self).setUp()
        self.view = view = api.content.get_view('view',
                                                self.portal.news,
                                                self.request.clone())
        self.tree = lxml.html.fromstring(view())

    def test_magazine_home_section_nav(self):
        nav = self.tree.cssselect('nav.canvas-subnav')[0]
        self.assertEqual(
            [x.text for x in nav.iterchildren()],
            ['All news', 'Company News', 'Press Mentions'])

    def test_magazine_home_items(self):
        items = self.tree.cssselect('article.item')
        self.assertEqual(len(items), 10)

    def test_magazine_trending(self):
        self.assertEqual(0, len(self.view.trending_items()))
        hit = api.content.get_view(
            'mustread-hit',
            self.portal.news['etiam-augue'],
            self.request.clone())
        hit()
        # re-init to bypass memoize
        view = api.content.get_view('view',
                                    self.portal.news,
                                    self.request.clone())
        self.assertEqual(1, len(view.trending_items()))
