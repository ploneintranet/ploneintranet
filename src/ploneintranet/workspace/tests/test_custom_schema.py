from ploneintranet.workspace.tests.base import BaseTestCase
from ploneintranet.workspace.behaviors.image import IImageField
from ploneintranet.workspace.behaviors.file import IFileField
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone import api


class TestCustomSchema(BaseTestCase):

    def test_custom_image_schema(self):
        workspace = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='Welcome to my workspace'
        )
        image = api.content.create(
            workspace,
            'Image',
            title='An image',
        )

        self.assertTrue(IImageField.providedBy(image))
        primary = IPrimaryFieldInfo(image)
        self.assertFalse(primary.field.required)

    def test_custom_file_schema(self):
        workspace = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='Welcome to my workspace'
        )
        thefile = api.content.create(
            workspace,
            'File',
            title='An file',
        )

        self.assertTrue(IFileField.providedBy(thefile))
        primary = IPrimaryFieldInfo(thefile)
        self.assertFalse(primary.field.required)
