from Products.Five import BrowserView


class DownloadFileVersion(BrowserView):
    """ Helper method replacing the file_download_version skin script of
        CMFEditions modified to work with Dexterity Blob file types
    """
    def __call__(self, version_id=1):

        obj = self.context.portal_repository.retrieve(
            self.context, version_id).object
        self.request.RESPONSE.setHeader('Content-Type',
                                        obj.file.contentType)
        self.request.RESPONSE.setHeader('Content-Length',
                                        obj.file.getSize())
        self.request.RESPONSE.setHeader('Content-Disposition',
                                        'attachment;filename="%s"' %
                                        (obj.file.filename))

        return obj.file.data
