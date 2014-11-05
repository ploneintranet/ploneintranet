import unittest
import transaction
from plone.uuid.interfaces import IUUID
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_ID
from ..testing import PLONEINTRANET_async_FUNCTIONAL_TESTING
from ..demo.tasks import create_content


class TestContentCreation(unittest.TestCase):

    layer = PLONEINTRANET_async_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def tearDown(self):
        setRoles(self.portal, TEST_USER_ID, ['Member'])

    def test_content_creation(self):
        login(self.portal, TEST_USER_NAME)
        self.assertNotIn('foo', self.portal)
        result = create_content.delay(
            self.portal,
            'Document',
            'foo',
            setTitle=u"Foo",
            setDescription=u"Just a test page",
            setText=u"<p>Hello <em>world</em>!</p>"
        )
        self.assertNotIn('foo', self.portal)
        try:
            transaction.commit()
        except AssertionError:
            # do not want our test to be pollutes by assert made in 
            # transaction._manager
            pass
        result = result.get()
        self.assertIn('foo', self.portal)
        self.assertEqual(result, IUUID(self.portal['foo']))
        logout()

    def test_content_creation_in_dir(self):
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'test-f')
        folder = self.portal['test-f']
        folder.setTitle('Test folder')
        self.assertNotIn('foo', folder)
        result = create_content.delay(
            folder,
            'Document',
            'foo',
            setTitle=u"Foo",
            setDescription=u"Just a test page",
            setText=u"<p>Hello <em>world</em>!</p>"
        )
        self.assertNotIn('foo', folder)
        try:
            transaction.commit()
        except AssertionError:
            # do not want our test to be pollutes by assert made in 
            # transaction._manager
            pass
        result = result.get()
        self.assertIn('foo', folder)
        self.assertEqual(result, IUUID(folder['foo']))
        logout()
