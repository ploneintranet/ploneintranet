""" Convert the HTML in a field of an object to a PDF, using
collective.documentviewer and save it on the object.
"""
from Acquisition import aq_inner
from BeautifulSoup import BeautifulSoup
from PIL import Image
from collective.documentviewer.convert import Converter
from collective.documentviewer.convert import docsplit
from collective.documentviewer.settings import GlobalSettings
from collective.documentviewer.settings import Settings
from collective.documentviewer.utils import getDocumentType
from collective.documentviewer.utils import getPortal
from logging import getLogger
from plone import api
from plone.app.blob.field import ImageField
from ploneintranet.workspace.config import PDF_VERSION_KEY
from ploneintranet.workspace.config import PREVIEW_IMAGES_KEY
from ploneintranet.workspace.config import THUMBNAIL_KEY
from urllib2 import urlparse
from zope.annotation import IAnnotations

import codecs
import httplib
import os

logger = getLogger('collective.documentviewer')


class HTMLConverter(Converter):

    def __init__(self, context):
        self.context = aq_inner(context)
        self.settings = Settings(self.context)
        self.filehash = None
        self.blob_filepath = None
        self.gsettings = GlobalSettings(getPortal(context))
        self.storage_dir = self.get_storage_dir()
        self.doc_type = getDocumentType(
            self.context, self.gsettings.auto_layout_file_types)

    def convert_virtual_url(self, url):
        request = self.context.REQUEST
        virtual_url_parts = request.get('VIRTUAL_URL_PARTS')
        portal = api.portal.get()
        if not virtual_url_parts:
            portal_url = portal.absolute_url()
            if url.startswith(portal_url):
                server_url = request.get('SERVER_URL')
                return str(url.replace(server_url, ''))
            else:
                return url

        virtual_host, virtual_root, virtual_path = virtual_url_parts

        if url.startswith(virtual_host):
            path = url[len(virtual_host) + len(virtual_root):]
            url = '/{}{}'.format(portal.getId(), path)

        return url

    def get_local_image(self, path):
        try:
            img_obj = self.context.restrictedTraverse(path)
        except (KeyError, AttributeError) as e:
            logger.warn('Could not get image object for {0}: '
                        'KeyError {1}'.format(path, e))
            return (None, 0, 0)
        if not img_obj:
            logger.warn('Empty image object: %s' % path)
            return (None, 0, 0)
        if not hasattr(img_obj, 'image'):
            # doesn't seem to be a blob image
            logger.warn('Could not get image data: %s' % path)
            return (None, 0, 0)
        img_data = img_obj.image.data
        width, height = img_obj.image.getImageSize()
        return (img_data, width, height)

    def extract_images(self, soup, tempdir):
        index = 0
        for img in soup.body.findAll('img'):
            if not img.get('src'):
                img['src'] = ''
                continue
            img['src'] = self.convert_virtual_url(img['src'])
            width = 0
            height = 0
            img_data = None
            if img['src'].startswith('//'):
                img['src'] = 'http:' + img['src']
            # local image
            elif img['src'].startswith('/'):
                img_data, width, height = \
                    self.get_local_image(img['src'])
            # remote image
            if img['src'].startswith('http'):
                _, remote_server, img_path, _, _, _ = urlparse.urlparse(
                    img['src'])
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
            img_file = open(os.path.join(tempdir, img_id), 'wb')
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
            img['src'] = os.path.join('images', img_id)
        return soup

    def html_dump(self, filename):
        """ Dump the html from the text field of an object along with any
        referenced images to a temporary folder.
        """
        text_field = self.context.text
        if hasattr(text_field, 'output'):
            text = text_field.output
        else:
            text = ''

        soup = BeautifulSoup(text)

        if not soup.html:
            if not soup.body:
                frame = BeautifulSoup(
                    '<html><head><meta name="created"></head><body>'
                    '</body></html>'
                )
            else:
                frame = BeautifulSoup(
                    '<html><head><meta name="created"></head></html>')
            frame.body.contents.extend(soup.contents)
            soup = frame

        output_dir = self.storage_dir

        if soup.body.img:
            tempdir = os.path.join(output_dir, 'images')
            os.mkdir(tempdir)
            soup = self.extract_images(soup, tempdir)

        html = unicode(soup)

        path = os.path.join(output_dir, filename)
        with codecs.open(path, 'w+', 'utf-8') as html_file:
            html_file.write(html)
        return path

    def run_conversion(self):
        file_id = 'dump'
        ext = '.html'
        filename = file_id + ext
        inputfilepath = self.html_dump(filename)
        if not inputfilepath:
            return

        cmd = [
            docsplit.binary, 'pdf', inputfilepath, '--output', self.storage_dir
        ]
        docsplit._run_command(cmd)
        pdf_path = os.path.join(self.storage_dir, file_id + '.pdf')
        annotations = IAnnotations(self.context)
        gsettings = self.gsettings
        sizes = (
            ('large', gsettings.large_size),
            ('normal', gsettings.normal_size),
            ('small', gsettings.thumb_size),
        )
        outputfilepath = os.path.join(self.storage_dir, file_id + '.pdf')
        with codecs.open(outputfilepath, 'r') as pdf_file:
            annotations[PDF_VERSION_KEY] = pdf_file.read()

        docsplit.dump_images(
            pdf_path, self.storage_dir, sizes=sizes, format='gif')

        thumb_dir = os.path.join(self.storage_dir, 'small')
        thumbnails = sorted(os.listdir(thumb_dir))
        preview_dir = os.path.join(self.storage_dir, 'large')
        previews = sorted(os.listdir(preview_dir))
        previewdata = []
        thumbdata = []
        for filename in previews[:20]:
            IF = ImageField()
            with open(os.path.join(preview_dir, filename)) as img:
                IF.set(self.context, img.read())
                previewdata.append(IF)
        for filename in thumbnails[:20]:
            IF = ImageField()
            with open(os.path.join(thumb_dir, filename)) as img:
                IF.set(self.context, img.read())
                thumbdata.append(IF)

        annotations[PREVIEW_IMAGES_KEY] = previewdata
        annotations[THUMBNAIL_KEY] = thumbdata


def generate_pdf(obj, event=None):
    """ Generate the previews for a content type. We need our own subscriber as
    c.dv insists on checking for its custom layout. Also we want our own async
    mechanism, it is using this method.

    :param obj: The Plone content object to get preview URLs for
    :type obj: A Plone content object
    :return: Does not return anything.
    :rtype: None
    """
    converter = HTMLConverter(obj)
    converter()
