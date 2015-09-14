import os
from Products.Five import BrowserView
from ploneintranet.docconv.client.interfaces import IDocconv
from collective.documentviewer.settings import Settings
from webdav.common import rfc1123_date
from plone.app.blob.iterators import BlobStreamIterator
from plone.app.blob.utils import openBlob
from plone.app.blob.download import handleRequestRange


class ImageView(BrowserView):
    """ Base class for views that render docconv related images """

    preview_type = None

    def pages_count(self):
        return len(self._get_data() or [])

    def available(self):
        """ check if we have a preview image """
        raise NotImplementedError

    def message(self):
        """ check if there is a message from the conversion """
        raise NotImplementedError

    def _get_data(self):
        raise NotImplementedError

    def __call__(self):
        self.page = int(self.request.get('page', 1))
        self.settings = Settings(self.context)
        r = self.request.response

        if self.preview_type not in ('large', 'normal', 'small'):
            self.preview_type = 'small'
        if self.page is None:
            self.page = 1
        filepath = u'%s/dump_%s.%s' % (self.preview_type,
                                       self.page,
                                       self.settings.pdf_image_format)
        blob = self.settings.blob_files[filepath]
        blobfi = openBlob(blob)
        length = os.fstat(blobfi.fileno()).st_size
        blobfi.close()
        ext = os.path.splitext(os.path.normcase(filepath))[1][1:]
        if ext == 'txt':
            ct = 'text/plain'
        else:
            ct = 'image/%s' % ext

        r.setHeader('Content-Type', ct)
        r.setHeader('Last-Modified',
                    rfc1123_date(self.context._p_mtime))
        r.setHeader('Accept-Ranges', 'bytes')
        r.setHeader("Content-Length", length)
        request_range = handleRequestRange(self.context,
                                           length,
                                           self.request,
                                           self.request.response)
        return BlobStreamIterator(blob, **request_range)


class PreviewView(ImageView):

    preview_type = 'normal'

    def _get_data(self):
        return IDocconv(self.context).get_previews()

    def available(self):
        return IDocconv(self.context).has_previews()

    def message(self):
        return IDocconv(self.context).conversion_message()


class ThumbnailView(ImageView):

    preview_type = 'small'

    def _get_data(self):
        return IDocconv(self.context).get_thumbs()

    def available(self):
        return IDocconv(self.context).has_thumbs()


# class PdfNotAvailableView(BrowserView):
#     pass


# class PdfRequestView(BrowserView):

#     def __call__(self):
#         docconv = IDocconv(self.context)
#         if docconv.generate_all():
#             self.message = (
#                 'Your request for a PDF version of this document '
#                 'is being processed. It will take a few minutes until it is '
#                 'ready for download. Please check back later.')
#         else:
#             self.message = (
#                 'A PDF version of this document has been requested'
#                 ' and is in preparation. It will be available for download '
#                 'shortly. Please select the download button from the gearbox'
#                 ' again in a few minutes.')
#         return super(PdfRequestView, self).__call__()


# class PdfView(BrowserView):

#     def __call__(self):
#         docconv = IDocconv(self.context)
#         if not docconv.has_pdf():
#             return self.request.RESPONSE.redirect(
#                 self.context.absolute_url() + '/pdf-not-available')

#         pdfversion = docconv.get_pdf()
#         R = self.request.RESPONSE
#         R.setHeader('content-type', 'application/pdf')
#         R.setHeader(
#             'content-disposition',
#             'attachment; filename="%s"' % '.'.join(
#                 (self.context.getId(), u'pdf')).encode('utf8'))
#         if isinstance(pdfversion, basestring):
#             length = len(pdfversion)
#             R.setHeader('content-length', length)
#             return pdfversion
#         else:
#             length = pdfversion.get_size(self.context)
#             R.setHeader('content-length', length)
#             blob = pdfversion.get(self.context, raw=True)
#             charset = 'utf-8'
#             return blob.index_html(
#                 REQUEST=self.request, RESPONSE=R,
#                 charset=charset
#             )
