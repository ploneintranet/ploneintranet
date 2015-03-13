from Products.ATContentTypes.content import file
from Products.ATContentTypes.content import image
from ploneintranet.attachments.attachments import IAttachmentStorage
from zope.component import createObject
from zope.container.interfaces import DuplicateIDError

from ploneintranet.attachments.testing import IntegrationTestCase


class TestAttachmentStorage(IntegrationTestCase):
    """ Test the IAttachmentStorage adapter
    """

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
