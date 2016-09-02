from zope.annotation import IAnnotations
from ploneintranet.workspace.config import PDF_VERSION_KEY
from Products.Five import BrowserView


class PdfView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._annotations = IAnnotations(context)

    def _get_data(self, key):
        data = self._annotations.get(key)
        return data

    def get_pdf(self):
        return self._get_data(PDF_VERSION_KEY)

    def has_pdf(self):
        return self.is_available(self.context, data_type='pdf')

    def is_available(self, obj, data_type='preview'):
        if data_type == 'pdf':
            annotations = IAnnotations(obj)
            if annotations.get(PDF_VERSION_KEY):
                return True
            else:
                return False

    def __call__(self):
        if not self.has_pdf():
            return self.request.RESPONSE.redirect(
                self.context.absolute_url() + '/pdf-not-available')

        pdfversion = self.get_pdf()
        R = self.request.RESPONSE
        R.setHeader('content-type', 'application/pdf')
        R.setHeader(
            'content-disposition',
            'attachment; filename="%s"' % '.'.join(
                (self.context.getId(), u'pdf')).encode('utf8'))
        if isinstance(pdfversion, str):
            length = len(pdfversion)
            R.setHeader('content-length', length)
            return pdfversion
        else:
            length = pdfversion.get_size(self.context)
            R.setHeader('content-length', length)
            return pdfversion.download(self.context)
