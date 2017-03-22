# coding=utf-8
from json import dumps
from json import loads
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.content.browser.file import FileUploadView
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from zope.publisher.browser import BrowserView


class VerifyPasswordResetAllowed(BrowserView):
    """
        Check if users are allowed to reset their password.
        Redirect to given URL otherwise.
        This mimicks the way the old rejectAnonymous script from
        Archetypes used to work.
    """

    def __call__(self, redirect_url=''):
        try:
            enable_password_reset = api.portal.get_registry_record(
                'ploneintranet.userprofile.enable_password_reset')
        except InvalidParameterError:
            enable_password_reset = False
        if not enable_password_reset:
            message = _(u'Resetting your own password is not supported.')
            api.portal.show_message(message, self.request, 'error')
            if not redirect_url:
                redirect_url = self.context.absolute_url()
            self.request.response.redirect(redirect_url)
        return True


class ImagePickerJson(BrowserView):
    """
    Returns Images in current Folder in a redactor json format
    [
        {
            "id": 1,
            "title": "Air Canada Landmark Agreement",
            "url": "/media/air-canada-landmark-agreement.jpg",
            "thumb": "/media/air-canada-landmark-agreement.jpg"
        },
        {
            "id": 2,
            "title": "A380",
            "url": "/media/air-france-a380.jpg",
            "thumb": "/media/air-france-a380.jpg",
        }
    ]
    """

    def __call__(self):
        catalog = api.portal.get_tool('portal_catalog')
        results = catalog(
            portal_type='Image',
            path={'query': '/'.join(self.context.getPhysicalPath())}
        )
        images = [
            {
                'id': img['getId'],
                'title': img['Title'],
                'url': '%s/@@images/image/large' % img.getURL(),
                'thumb': '%s/@@images/image/preview' % img.getURL(),
            } for img in results
        ]
        return dumps(images)


class ImageFileUploadJson(FileUploadView):

    def __call__(self):
        '''
        '''
        data = loads(super(ImageFileUploadJson, self).__call__())
        data['url'] = data['url'] + u'/@@images/image/large'
        return dumps(data)
