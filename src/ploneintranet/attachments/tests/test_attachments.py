from Products.ATContentTypes.content import file
from Products.ATContentTypes.content import image
from ploneintranet.attachments.attachments import IAttachmentStorage
from ploneintranet.attachments.attachments import IAttachmentStoragable
from zope.component import createObject
from zope.interface import alsoProvides
from zope.container.interfaces import DuplicateIDError

from ploneintranet.attachments.testing import IntegrationTestCase


class TestAttachmentStorage(IntegrationTestCase):
    """ Test the IAttachmentStorage adapter
    """

    def test_add(self):
        """ """
        doc1 = createObject('Document')
        alsoProvides(doc1, IAttachmentStoragable)
        attachments = IAttachmentStorage(doc1)
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
        question = createObject('Document')
        alsoProvides(question, IAttachmentStoragable)
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
