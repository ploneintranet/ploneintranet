from Products.Five import BrowserView

from ploneintranet import api as pi_api


class ImageView(BrowserView):
    """ Base class for views that render preview related images """

    def pages_count(self):
        return len(self._get_data() or [])

    def available(self):
        """ check if we have a preview image """
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
            R.setHeader(
                'content-disposition',
                'inline; filename="{0}_preview.jpg"'.format(
                    self.context.getId().encode('utf8'))
            )
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
    """

    """

    def _get_data(self):
        return pi_api.previews.get(self.context)

    def available(self):
        return pi_api.previews.has_previews(self.context)


class ThumbnailView(ImageView):
    def _get_data(self):
        return pi_api.previews.get_thumb(self.context)

    def available(self):
        return pi_api.previews.has_thumb(self.context)
