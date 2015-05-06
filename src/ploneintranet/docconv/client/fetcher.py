import httplib
import random
import shutil
import string
from io import BytesIO
from logging import getLogger
from os import path
from os import walk
from urllib2 import urlparse
from zipfile import ZipFile
from tempfile import mkdtemp
from BeautifulSoup import BeautifulSoup
from PIL import Image

from plone.app.blob.field import FileField
from plone.app.blob.field import ImageField
from plone.app.contenttypes.interfaces import IDocument
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IBaseContent
from zope.annotation import IAnnotations
from zope.component.hooks import getSite

from ploneintranet.docconv.client.config import (
    DOCCONV_EXCLUDE_TYPES as EXCLUDE_TYPES,
    PDF_VERSION_KEY,
    PREVIEW_IMAGES_KEY,
    THUMBNAIL_KEY,
    PREVIEW_MESSAGE_KEY,
)
from ploneintranet.docconv.client.exceptions import ServerError
from ploneintranet.docconv.client.exceptions import ConfigError
from ploneintranet.docconv.client.interfaces import IPreviewFetcher
from slc.docconv.convert import convert_to_raw

logger = getLogger(__name__)


def get_server_url():
    site = getSite()
    portal_properties = getToolByName(site, 'portal_properties')
    site_properties = portal_properties.site_properties
    return site_properties.getProperty('docconv_url')


class BasePreviewFetcher(object):
    """ Adapter that fetches preview images and pdf version for an object from
    the docconv service """

    typeinfo = {'html': {'ext': '.html', 'mime': 'text/html', },
                'zip': {'ext': '.zip', 'mime': 'application/octetstream', },
                }
    body_tmpl = """--%(boundary)s
Content-Disposition: form-data; name="filedata"; filename="%(id)s%(ext)s"
Content-Type: %(mime)s

%(data)s
--%(boundary)s--
"""

    def __init__(self, context):
        self.context = context
        self.request = None
        if hasattr(self.context, 'REQUEST'):
            self.request = self.context.REQUEST

    def getPayload(self):
        """
        Get mimetype and data for associated file
        """
        if IBaseContent.providedBy(self.context):
            primary_field = self.context.getPrimaryField()
            mimetype = self.context.getContentType()
            data = primary_field.get(self.context)
        else:
            primary_field = IPrimaryFieldInfo(self.context).value
            mimetype = primary_field.contentType
            data = primary_field.data

        return mimetype, str(data)

    def __call__(self):
        annotations = IAnnotations(self.context)

        # get the contents of the context
        mimetype, payload = self.getPayload()

        if mimetype:
            basetype = mimetype.split('/')[0]
        else:
            basetype = None

        if basetype in EXCLUDE_TYPES:
            logger.warn('Type {0} is in excluded types, '
                        'skipping {1}'.format(
                            basetype,
                            self.context.getId())
                        )
            annotations[PREVIEW_MESSAGE_KEY] = ('There is no preview for this '
                                                'file type')
            return

        try:
            converted = self.convert_on_server(payload, mimetype)
        except ServerError as e:
            if e.args and e.args[0].startswith("Error connecting"):
                annotations[PREVIEW_MESSAGE_KEY] = (
                    'Could not contact conversion server')
            else:
                annotations[PREVIEW_MESSAGE_KEY] = (
                    'Sorry, this document type cannot be converted. There is '
                    'no preview available.')
            return
        except ConfigError:
            converted = self.convert_locally(payload, mimetype)

        pdfdata = FileField()
        pdfdata.set(self.context, converted['pdfs'][0])
        previewdata = []
        thumbdata = []
        for filedata in converted['previews'][:20]:
            IF = ImageField()
            IF.set(self.context, filedata)
            previewdata.append(IF)
        for filedata in converted['thumbnails'][:20]:
            IF = ImageField()
            IF.set(self.context, filedata)
            thumbdata.append(IF)

        annotations[PDF_VERSION_KEY] = pdfdata
        annotations[PREVIEW_IMAGES_KEY] = previewdata
        annotations[THUMBNAIL_KEY] = thumbdata

    def convert_locally(self, payload, datatype):
        try:
            return convert_to_raw(self.context.getId(), payload, datatype)
        except IOError as e:
            if 'docsplit not found' in e:
                raise ConfigError("docsplit is not available")
            else:
                raise e

    def unpack_zipdata(self, zipdata):
        stream = BytesIO(zipdata)
        fzip = ZipFile(stream)
        pdfs = [x.filename for x in fzip.filelist
                if x.filename.endswith('.pdf')]
        if not pdfs:
            raise ServerError(
                'Conversion returned zip containing no pdf files')

        thumbnails = sorted(
            [x.filename for x in fzip.filelist
                if x.filename.startswith('small/') and x.filename != 'small/'],
            key=lambda x: int(x.split('.')[0].split('_')[-1]))
        previews = sorted(
            [x.filename for x in fzip.filelist
                if x.filename.startswith('large/') and x.filename != 'large/'],
            key=lambda x: int(x.split('.')[0].split('_')[-1]))
        converted = {
            'pdfs': [fzip.read(pdfs[0])],
            'thumbnails': [fzip.read(filename)
                           for filename in thumbnails[:20]],
            'previews': [fzip.read(filename) for filename in previews[:20]],
        }
        fzip.close()
        stream.close()
        return converted

    def convert_on_server(self, payload, datatype):
        docconv_url = get_server_url()
        if not docconv_url:
            # logger.error('No docconv_url in site_properties')
            raise ConfigError(
                'No docconv_url specified, can not fetch previews')
            # return None
        schema, docconv_server, docconv_path, _, _, _ = urlparse.urlparse(
            docconv_url)

        boundary = '-' * 28 + ''.join(
            [random.choice(string.digits) for x in range(28)])
        headers = {'Content-Type': 'multipart/form-data;'
                   'boundary={0}'.format(boundary)}

        if datatype not in self.typeinfo:
            ext = ''
            mime = datatype
        else:
            ext = self.typeinfo[datatype]['ext']
            mime = self.typeinfo[datatype]['mime']
        body = self.body_tmpl % {
            'id': self.context.getId().replace(' ', '-'),
            'boundary': boundary,
            'ext': ext,
            'mime': mime,
            'data': payload,
        }

        try:
            if schema == 'http':
                conn = httplib.HTTPConnection(docconv_server, timeout=300)
            elif schema == 'https':
                conn = httplib.HTTPSConnection(docconv_server, timeout=300)
            else:
                raise ConfigError('Docconv url has unknown schema:'
                                  '{0}'.format(docconv_url))
            conn.request('POST', docconv_path, body, headers)
            resp = conn.getresponse()
        except Exception as e:
            raise ServerError('Error connecting to %s: %s' % (docconv_url, e))
        if not resp.status == 200:
            raise ServerError('Conversion returned {0}: {1}'.format(
                resp.status, resp.reason))
        zipdata = resp.read()
        conn.close()

        data = self.unpack_zipdata(zipdata)

        return data


class PreviewFetcher(BasePreviewFetcher):
    pass


class HtmlPreviewFetcher(BasePreviewFetcher):
    """ Base class for fetching previews for html based content like Documents,
        implements image handling and the like """

    def convertVirtualUrl(self, url):
        if not self.virtual_url_parts:
            return url

        virtual_host, virtual_root, virtual_path = self.virtual_url_parts

        if url.startswith(virtual_host):
            url = url[len(virtual_host):]
        elif url.startswith('http'):
            return url

        absolute = url.startswith('/')

        urlpath = url.split('/')

        if absolute and urlpath[1] == virtual_root:
            urlpath = self.vr_path + urlpath[2:]

        return '/'.join(urlpath)

    def extractImages(self, soup, tempdir):
        index = 0
        for img in soup.body.findAll('img'):
            if not img.get('src'):
                img['src'] = ''
                continue
            img['src'] = self.convertVirtualUrl(img['src'])
            width = 0
            height = 0
            if img['src'].startswith('//'):
                img['src'] = 'http:' + img['src']
            # local image
            elif img['src'].startswith('/'):
                img_data, width, height = self.getLocalImage(img['src'])
            # remote image
            if img['src'].startswith('http'):
                _, remote_server, img_path, _, _, _ = urlparse.urlparse(
                    img['src'])
                img_data = None
                try:
                    conn = httplib.HTTPConnection(remote_server)
                    conn.request('GET', img_path)
                    resp = conn.getresponse()
                    if not resp.status == 200:
                        logger.warn('Could not get image {0}: {1} {2}'.format(
                                    img['src'], resp.status, resp.reason))
                    else:
                        img_data = resp.read()
                except Exception as e:
                    logger.warn('Error getting remote image {0}: {1}'.format(
                        img['src'], e))
                conn.close()

            if not img_data:
                continue

            img_orig_id = img['src'].split('/')[-1]
            img_ext = img_orig_id.split('.')[-1]
            if img_ext == img_orig_id:
                img_ext = 'dat'
            img_id = 'image%d.%s' % (index, img_ext)
            index += 1
            img_file = open(path.join(tempdir, img_id), 'wb')
            img_file.write(img_data)
            img_file.close()
            if 'width' not in img or 'height' not in img:
                try:
                    img_obj = Image.open(img_file.name)
                    width, height = img_obj.size
                except Exception as e:
                    logger.warn('Could not get image size for {0}: {1}'.format(
                                img['src'], e))
            if width and 'width' not in img:
                img['width'] = width
            if height and 'height' not in img:
                img['height'] = height
            img['src'] = img_id
        return soup

    def getLocalImage(self, path):
        # portal = getToolByName(self.context, 'portal_url').getPortalObject()
        # absolute = path.startswith('/')
        img_path = path.split('/')
        try:
            # if absolute:
            #     img_obj = portal.restrictedTraverse(img_path)
            # else:
            img_obj = self.context.restrictedTraverse(img_path)
        except (KeyError, AttributeError) as e:
            logger.warn('Could not get image object for {0}: '
                        'KeyError {1}'.format(img_path, e))
            return (None, 0, 0)
        if not img_obj:
            logger.warn('Empty image object: %s' % img_path)
            return (None, 0, 0)
        if not hasattr(img_obj, 'getBlobWrapper'):
            # doesn't seem to be a blob image
            logger.warn('Could not get image data: %s' % img_path)
            return (None, 0, 0)
        img_data = img_obj.getBlobWrapper().getBlob().open().read()

        return (img_data, img_obj.getWidth(), img_obj.getHeight())

    def getZipData(self, tempdir):
        stream = BytesIO()
        zipped = ZipFile(stream, 'w')
        for entry in walk(tempdir):
            relpath = path.relpath(entry[0], tempdir)
            if not entry[0] == tempdir:
                # if it's not the top dir we want to add it
                zipped.write(entry[0], relpath.encode('CP437'))
            # we want to add the contained files except the zip file itself
            for filename in entry[2]:
                relative = path.join(relpath, filename)
                zipped.write(path.join(entry[0], filename), relative)
        zipped.close()
        return stream.getvalue()

    def getHtml(self):
        return self.context.text

    def getPayload(self):
        html = self.getHtml()
        if not html:
            return 'html', '<html><body></body></html>'

        soup = BeautifulSoup(html)

        if not soup.html:
            if not soup.body:
                frame = BeautifulSoup('<html><body></body></html>')
            else:
                frame = BeautifulSoup('<html></html>')
            frame.body.contents.extend(soup.contents)
            soup = frame

        if not soup.body.img:
            return 'text/html', str(soup)
        else:
            tempdir = mkdtemp()

            soup = self.extractImages(soup, tempdir)

            html_file = open(
                path.join(tempdir,
                          '.'.join((self.context.getId(), 'html'))),
                'w')
            html_file.write(str(soup))
            html_file.close()

            zipdata = self.getZipData(tempdir)
            shutil.rmtree(tempdir)

            return 'application/zip', zipdata

    def __call__(self, virtual_url_parts, vr_path):
        self.virtual_url_parts = virtual_url_parts
        self.vr_path = vr_path
        if not self.getHtml():
            logger.info('Skipping empty object {0}'.format(
                '/'.join(self.context.getPhysicalPath())))
            return
        return super(HtmlPreviewFetcher, self).__call__()


def fetchPreviews(context, virtual_url_parts=[], vr_path=''):
    """ calls the docconv service and stores pdf and preview images on the
    object """
    fetcher = IPreviewFetcher(context)
    if IDocument.providedBy(context):
        if not virtual_url_parts or not vr_path:
            logger.warn('No virtual hosting info, cannot get local images! '
                        'Skipping %s' % '/'.join(context.getPhysicalPath()))
            return
        fetcher_args = (virtual_url_parts, vr_path)
    else:
        fetcher_args = ()
    try:
        fetcher(*fetcher_args)
    except Exception as e:
        logger.warn('fetchPreviews failed: {0}'.format(e))
        return
    context.reindexObject()
