# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.news.testing import FunctionalTestCase
import lxml


class MagazineTest(FunctionalTestCase):
    '''
    Because sqlalchemy gives threading errors when hit via ZServer,
    we fake browser interactions directly on the testing thread itself.

    This is just a minimal smoke test to prove that the view does not error.
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


class PublisherTest(FunctionalTestCase):
    '''
    Because sqlalchemy gives threading errors when hit via ZServer,
    we fake browser interactions directly on the testing thread itself.

    This is just a minimal smoke test to prove that the view does not error.
    '''

    def setUp(self):
        super(PublisherTest, self).setUp()
        self.view = view = api.content.get_view('publisher',
                                                self.portal.news,
                                                self.request.clone())
        self.tree = lxml.html.fromstring(view())

    def test_sidebar_section(self):
        heading = self.tree.cssselect('form#listing-company-news h4')[0]
        self.assertEqual(heading.text.strip(), 'Company News')

    def test_sidebar_item(self):
        heading = self.tree.cssselect(
            'form#listing-company-news label h4')[0]
        self.assertEqual(heading.text.strip(), 'Etiam augue.')


class EditingTest(FunctionalTestCase):
    '''
    Because sqlalchemy gives threading errors when hit via ZServer,
    we fake browser interactions directly on the testing thread itself.

    This is just a minimal smoke test to prove that the view does not error.
    '''

    def setUp(self):
        super(EditingTest, self).setUp()
        self.item = item = self.portal.news['etiam-augue']
        self.view = view = api.content.get_view('edit.html',
                                                item,
                                                self.request.clone())
        self.tree = lxml.html.fromstring(view())

    def test_image_visibility(self):
        checkbox = self.tree.xpath('//input[@name="article_image"]')[0]
        self.assertEqual(checkbox.value, 'selected')

    def test_sidebar_section(self):
        '''Verify that sidebar is loaded in edit view'''
        heading = self.tree.cssselect('form#listing-company-news h4')[0]
        self.assertEqual(heading.text.strip(), 'Company News')
