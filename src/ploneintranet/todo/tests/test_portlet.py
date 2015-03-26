from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.lifecycleevent import modified
from plone import api
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletManager
from plone.namedfile.file import NamedBlobImage
from ..behaviors import IMustRead
from ..portlets import latest
from ..testing import IntegrationTestCase


LOGO = (
    'GIF89a\x10\x00\x10\x00\xd5\x00\x00\xff\xff\xff\xff\xff\xfe\xfc\xfd\xfd'
    '\xfa\xfb\xfc\xf7\xf9\xfa\xf5\xf8\xf9\xf3\xf6\xf8\xf2\xf5\xf7\xf0\xf4\xf6'
    '\xeb\xf1\xf3\xe5\xed\xef\xde\xe8\xeb\xdc\xe6\xea\xd9\xe4\xe8\xd7\xe2\xe6'
    '\xd2\xdf\xe3\xd0\xdd\xe3\xcd\xdc\xe1\xcb\xda\xdf\xc9\xd9\xdf\xc8\xd8\xdd'
    '\xc6\xd7\xdc\xc4\xd6\xdc\xc3\xd4\xda\xc2\xd3\xd9\xc1\xd3\xd9\xc0\xd2\xd9'
    '\xbd\xd1\xd8\xbd\xd0\xd7\xbc\xcf\xd7\xbb\xcf\xd6\xbb\xce\xd5\xb9\xcd\xd4'
    '\xb6\xcc\xd4\xb6\xcb\xd3\xb5\xcb\xd2\xb4\xca\xd1\xb2\xc8\xd0\xb1\xc7\xd0'
    '\xb0\xc7\xcf\xaf\xc6\xce\xae\xc4\xce\xad\xc4\xcd\xab\xc3\xcc\xa9\xc2\xcb'
    '\xa8\xc1\xca\xa6\xc0\xc9\xa4\xbe\xc8\xa2\xbd\xc7\xa0\xbb\xc5\x9e\xba\xc4'
    '\x9b\xbf\xcc\x98\xb6\xc1\x8d\xae\xbaFgs\x00\x00\x00\x00\x00\x00\x00\x00'
    '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    '\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x06z@\x80pH,\x12k\xc8$\xd2f\x04'
    '\xd4\x84\x01\x01\xe1\xf0d\x16\x9f\x80A\x01\x91\xc0ZmL\xb0\xcd\x00V\xd4'
    '\xc4a\x87z\xed\xb0-\x1a\xb3\xb8\x95\xbdf8\x1e\x11\xca,MoC$\x15\x18{'
    '\x006}m\x13\x16\x1a\x1f\x83\x85}6\x17\x1b $\x83\x00\x86\x19\x1d!%)\x8c'
    '\x866#\'+.\x8ca`\x1c`(,/1\x94B5\x19\x1e"&*-024\xacNq\xba\xbb\xb8h\xbeb'
    '\x00A\x00;'
)


class TestPortlet(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = api.content.create(
            type='Folder',
            title=u'News test',
            container=self.portal
        )
        self.news_items = []
        for i in xrange(0, 10):
            news_item = api.content.create(
                type='News Item',
                title=u'News {}'.format(i + 1),
                container=self.folder,
                text=u'<p>Hello <em>World</em>!</p>',
                image=NamedBlobImage(LOGO, filename=u'zpt.gif')
            )
            self.news_items.append(news_item)
            behavior = IMustRead(news_item)
            behavior.mustread = True
            modified(news_item)

    def _get_renderer(self):
        manager = getUtility(
            IPortletManager,
            name='plone.leftcolumn',
            context=self.portal
        )
        assignment = latest.Assignment(count=5)
        view = self.portal.restrictedTraverse('@@plone')
        return getMultiAdapter(
            (self.portal,
             self.portal.REQUEST,
             view,
             manager,
             assignment),
            IPortletRenderer
        )

    def test_rendering(self):
        renderer = self._get_renderer()
        html = renderer.render()
        self.assertIn(
            u"""<div class="news portlet" id="portlet-news">""",
            html
        )
        self.assertIn(
            u'news-test/news-',
            html
        )

    def test_data(self):
        renderer = self._get_renderer()
        latest = renderer.latest_news()
        self.assertEqual(
            api.content.get_uuid(latest[0]),
            api.content.get_uuid(self.news_items[-1])
        )

    def test_mark(self):
        renderer = self._get_renderer()
        item = renderer.latest_news()[0]
        mark_view = getMultiAdapter(
            (item, self.layer['request']),
            name=u'mark_read'
        )
        mark_view()
        # If you know a more elegant way to clear memoize, please change :)
        if hasattr(renderer, '_memojito_'):
            del renderer._memojito_
        self.assertNotIn(
            api.content.get_uuid(item),
            [api.content.get_uuid(c) for c in renderer.latest_news()]
        )
