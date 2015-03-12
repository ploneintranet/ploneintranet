from Products.ATContentTypes.content import file
from Products.ATContentTypes.content import image
from plone.app.testing import setRoles
from plone.app.testing.interfaces import TEST_USER_ID
from ploneintranet.attachments.attachments import IAttachmentStoragable
from ploneintranet.attachments.attachments import IAttachmentStorage
from zExceptions import NotFound
from zope.component import createObject
from zope.container.interfaces import DuplicateIDError

from ploneintranet.attachments.testing import IntegrationTestCase


class TestAttachmentStorage(IntegrationTestCase):
    """ Test the IAttachmentStorage adapter
    """

    def test_storageable(self):
        comment = createObject('plone.Comment')
        self.assertTrue(IAttachmentStoragable.providedBy(comment))
        question = createObject('slc.underflow.question')
        self.assertTrue(IAttachmentStoragable.providedBy(question))

    def test_add(self):
        """ """
        comment1 = createObject('plone.Comment')
        attachments = IAttachmentStorage(comment1)
        self.assertEqual(len(attachments.keys()), 0)
        self.assertEqual(len(attachments.values()), 0)
        f = file.ATFile('data.dat')
        attachments.add(f)
        self.assertEqual([k for k in attachments.keys()], [f.getId()])
        self.assertEqual([v for v in attachments.values()], [f])

        # DuplicateIDError is thrown when an object with the same id is
        # added again.
        self.assertRaises(DuplicateIDError, attachments.add, f)

        i = image.ATImage('image.jpg')
        attachments.add(i)
        self.assertEqual(len(attachments.keys()), 2)
        self.assertEqual(len(attachments.values()), 2)
        self.assertTrue(i.getId()in attachments.keys())
        self.assertTrue(i in attachments.values())

    def test_remove(self):
        """ """
        question = createObject('slc.underflow.question')
        attachments = IAttachmentStorage(question)
        self.assertEqual(len(attachments.keys()), 0)
        self.assertEqual(len(attachments.values()), 0)
        for fname in ['data1.dat', 'data2.dat']:
            attachments.add(file.ATFile(fname))
        self.assertEqual(len(attachments.keys()), 2)
        self.assertEqual(len(attachments.values()), 2)

        self.assertRaises(KeyError, attachments.remove, 'data3.dat')

        attachments.remove('data1.dat')
        self.assertEqual(len(attachments.keys()), 1)
        self.assertTrue('data2.dat' in attachments.keys())
        attachments.remove('data2.dat')
        self.assertEqual(len(attachments.keys()), 0)


class TestAttachmentTraverse(IntegrationTestCase):
    """ Test the ++attachment++ traversal namespace.
    """

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ('Manager',))
        id = self.portal.invokeFactory(
            'Folder',
            'workspace1',
            title=u"Workspace 1")
        self.workspace = self.portal._getOb(id)

    def test_traverse(self):
        id = self.workspace.invokeFactory(
            'slc.underflow.question',
            'question',
            title=u'Question')
        question = self.workspace._getOb(id)
        attachments = IAttachmentStorage(question)
        f = file.ATFile('data1.dat')
        attachments.add(f)

        response = self.portal.restrictedTraverse(
            '%s/++attachments++default/data1.dat'
            % ('/'.join(question.getPhysicalPath())))
        self.assertEqual(f, response)

        # Test traversal to a non-existing attachment
        self.assertRaises(
            NotFound,
            self.portal.restrictedTraverse,
            '%s/++attachments++default/non-existing.dat'
            % ('/'.join(question.getPhysicalPath())))

    def test_path(self):
        id = self.workspace.invokeFactory(
            'slc.underflow.question',
            'question',
            title=u'Question')
        question = self.workspace._getOb(id)
        attachments = IAttachmentStorage(question)
        f = file.ATFile('data1.dat')
        attachments.add(f)
        attachment_path = attachments.get('data1.dat').getPhysicalPath()

        self.assertEquals(
            '/'.join(attachment_path),
            '%s/++attachments++default/data1.dat'
            % ('/'.join(question.getPhysicalPath())))

        response = self.portal.restrictedTraverse(attachment_path)

        self.assertEqual(
            '/'.join(response.getPhysicalPath()),
            '/'.join(attachment_path))
