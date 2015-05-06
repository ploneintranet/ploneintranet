from Products.Five import BrowserView
from ploneintranet.docconv.client.interfaces import IDocconv


class ImageView(BrowserView):
    """ Base class for views that render docconv related images """

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
        page = int(self.request.get('page', 1))

        previews = self._get_data()
        if previews:
            if page - 1 >= len(previews):
                page = 0
            elif page < 1:
                page = 1
            imgdata = previews[page - 1]
            R = self.request.RESPONSE
            R.setHeader('content-type', 'image/jpeg')
            R.setHeader('content-disposition', 'inline; '
                        'filename="{0}_preview.jpg"'.format(
                            self.context.getId().encode('utf8')))
            if isinstance(imgdata, basestring):
                length = len(imgdata)
                R.setHeader('content-length', length)
                return imgdata
            else:
                length = imgdata.get_size(self.context)
                R.setHeader('content-length', length)
                blob = imgdata.get(self.context, raw=True)
                charset = 'utf-8'
                return blob.index_html(
                    REQUEST=self.request, RESPONSE=R,
                    charset=charset
                )

        self.request.RESPONSE.setStatus(404)
        return None


class PreviewView(ImageView):

    def _get_data(self):
        return IDocconv(self.context).get_previews()

    def available(self):
        return IDocconv(self.context).has_previews()

    def message(self):
        return IDocconv(self.context).conversion_message()


class ThumbnailView(ImageView):

    def _get_data(self):
        return IDocconv(self.context).get_thumbs()

    def available(self):
        return IDocconv(self.context).has_thumbs()


class PdfNotAvailableView(BrowserView):
    pass


class PdfRequestView(BrowserView):

    def __call__(self):
        docconv = IDocconv(self.context)
        if docconv.generate_all():
            self.message = (
                'Your request for a PDF version of this document '
                'is being processed. It will take a few minutes until it is '
                'ready for download. Please check back later.')
        else:
            self.message = (
                'A PDF version of this document has been requested'
                ' and is in preparation. It will be available for download '
                'shortly. Please select the download button from the gearbox'
                ' again in a few minutes.')
        return super(PdfRequestView, self).__call__()


class PdfView(BrowserView):

    def __call__(self):
        docconv = IDocconv(self.context)
        if not docconv.has_pdf():
            return self.request.RESPONSE.redirect(
                self.context.absolute_url() + '/pdf-not-available')

        pdfversion = docconv.get_pdf()
        R = self.request.RESPONSE
        R.setHeader('content-type', 'application/pdf')
        R.setHeader(
            'content-disposition',
            'attachment; filename="%s"' % '.'.join(
                (self.context.getId(), u'pdf')).encode('utf8'))
        if isinstance(pdfversion, basestring):
            length = len(pdfversion)
            R.setHeader('content-length', length)
            return pdfversion
        else:
            length = pdfversion.get_size(self.context)
            R.setHeader('content-length', length)
            blob = pdfversion.get(self.context, raw=True)
            charset = 'utf-8'
            return blob.index_html(
                REQUEST=self.request, RESPONSE=R,
                charset=charset
            )
