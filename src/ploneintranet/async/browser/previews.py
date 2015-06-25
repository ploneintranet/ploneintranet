from Products.Five import BrowserView
from plone.namedfile.utils import stream_data

from ploneintranet import api as pi_api


class PreviewView(BrowserView):
    """View providing thumbnail image of context
    """
    def __call__(self, page=1, scale='preview'):
        try:
            self.page = int(page)
        except ValueError:
            self.page = 1
        self.scale = scale
        img = self.get_data()
        imgdata = img.data
        R = self.request.RESPONSE
        R.setHeader('content-type', 'image/png')
        R.setHeader(
            'content-disposition',
            'inline; filename="{0}_preview.png"'.format(
                self.context.getId().encode('utf8'))
        )
        R.setHeader('content-length', imgdata.size)
        return stream_data(imgdata)

    def get_data(self):
        prev = pi_api.previews.get_previews(self.context, self.scale)
        return prev[self.page - 1]


class ThumbnailView(PreviewView):

    def get_data(self):
        thumb = pi_api.previews.get_thumbnail(self.context)
        return thumb
