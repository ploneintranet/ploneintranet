from datetime import datetime
from io import BytesIO

from ZPublisher.HTTPRequest import ZopeFieldStorage, FileUpload
from plone import api
from plone.app.contenttypes.content import Folder
from plone.app.testing import setRoles
from plone.app.testing.interfaces import TEST_USER_ID
from zope.interface import classImplements
from zope.interface import alsoProvides

from ploneintranet.attachments.attachments import IAttachmentStoragable
from ploneintranet.attachments.attachments import IAttachmentStorage
from ploneintranet.attachments.testing import IntegrationTestCase
from ploneintranet.attachments.utils import clean_up_temporary_attachments
from ploneintranet.attachments.utils import create_attachment
from ploneintranet.attachments.utils import extract_and_add_attachments
from ploneintranet.attachments.utils import pop_temporary_attachment

classImplements(Folder, IAttachmentStoragable)


class TestAttachments(IntegrationTestCase):
    """Test attachment related util methods."""

    def setUp(self):
        """ """
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        self.workspace = api.content.create(
            type='Folder',
            title=u"Test Workspace",
            container=portal)
        self.document = api.content.create(
            type='Document',
            title=u"Test document",
            container=self.workspace)
        alsoProvides(self.document, IAttachmentStoragable)

    def _create_test_file_field(self):
        field_storage = ZopeFieldStorage()
        field_storage.file = BytesIO('test')
        field_storage.filename = 'test.pdf'
        file_field = FileUpload(field_storage)
        return file_field

    def _create_test_temp_attachment(self, token):
        filename = "{0}-test.pdf".format(token)
        attachment = create_attachment(filename, '')
        return attachment

    def test_create_attachment(self):
        file_field = self._create_test_file_field()
        att = create_attachment(file_field.filename, file_field.read())
        self.assertTrue(att.file.size > 0)
        self.assertEquals(att.id, file_field.filename)

    def test_temporary_attachment(self):
        token = "{0}-{1}".format(
            TEST_USER_ID,
            datetime.utcnow().strftime('%Y%m%d%H%M%S%f'))
        attachment = self._create_test_temp_attachment(token)
        temp_attachments = IAttachmentStorage(self.workspace)
        temp_attachments.add(attachment)
        file_field = self._create_test_file_field()
        res = pop_temporary_attachment(self.workspace, file_field, token)
        self.assertEquals(res.id, attachment.id)
        self.assertTrue(res.file.size > 0)

        clean_up_temporary_attachments(self.workspace, maxage=0)
        self.assertEquals(len(temp_attachments.keys()), 0)

    def test_extract_and_add_attachments(self):
        file_field = self._create_test_file_field()
        extract_and_add_attachments(file_field, self.document)
        attachments = IAttachmentStorage(self.document)
        self.assertEquals(len(attachments.values()), 1)
        res = attachments.get(file_field.filename)
        self.assertEquals(res.id, file_field.filename)

    def test_extract_and_add_attachments_with_token(self):
        token = "{0}-{1}".format(
            TEST_USER_ID,
            datetime.utcnow().strftime('%Y%m%d%H%M%S%f'))
        temp_attachment = self._create_test_temp_attachment(token)
        temp_attachments = IAttachmentStorage(self.workspace)
        temp_attachments.add(temp_attachment)
        file_field = self._create_test_file_field()
        extract_and_add_attachments(
            file_field, self.document, self.workspace, token)
        attachments = IAttachmentStorage(self.document)
        self.assertEquals(len(attachments.values()), 1)
        self.assertTrue(file_field.filename in attachments.keys())
        res = attachments.get(file_field.filename)
        self.assertEquals(res.id, file_field.filename)
        self.assertTrue(
            '/'.join(res.getPhysicalPath()).startswith(
                '/'.join(self.workspace.getPhysicalPath())))
