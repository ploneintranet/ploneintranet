import logging
import os
import shutil
import subprocess
from os import path

from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five import BrowserView
from zope.interface import alsoProvides

logger = logging.getLogger(__name__)


class ConvertDocument(BrowserView):
    """Convert a document to pdf and preview images.

    Meant to be called from a Celery task.

    Note that we explicitly disable CSRF protection.  There is no form
    that we can fill in, so there is no authenticator token that we
    could check.  Alternative: create such a form anyway, GET it from
    a Celery task, parse the html to get the authenticator token, and
    POST to the form again.  Seems overkill.
    """

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        # Generate the filename and locations
        filename = self.context.getId()
        # TODO: This should probably
        storage_dir = '/tmp'
        if content_type == 'application/octetstream':
            filename_dump = path.join(
                gsettings.storage_location, '.'.join((filename, 'html')))
        else:
            filename_dump = path.join(
                gsettings.storage_location, filename)
            if filename_dump.endswith(filename):
                filename_dump = '.'.join([filename_dump, 'dat'])
        filename_pdf = path.join(storage_dir, 'converted.pdf')

        if not path.exists(storage_dir):
            mkdir_p(storage_dir)
        if path.exists(filename_dump):
            remove(filename_dump)
        filename_dump, filename_pdf = get_file_locations(
            filename, content_type, gsettings)
        docsplit = DocconvDocSplitSubProcess()
        docsplit.convert_to_pdf(filename_dump, filename_dump, storage_dir)
        return 'OK'


class DocconvDocSplitSubProcess(object):
    """Customised to limit the number of pages"""

    default_paths = ['/bin', '/usr/bin', '/usr/local/bin']
    if os.name == 'nt':
        bin_name = 'docsplit.exe'
    else:
        bin_name = 'docsplit'

    def __init__(self):
        self.binary = self._findbinary()

    def dump_images(self, filepath, output_dir, sizes, format, lang='eng',
                    limit=20):
        # docsplit images pdf.pdf --size 700x,300x,50x
        # --format gif --output
        pages = self.get_num_pages(filepath)
        if pages < limit:
            limit = pages
        cmd = [self.binary, "images", filepath,
               '--language', lang,
               '--size', ','.join([str(s[1]) + 'x' for s in sizes]),
               '--format', format,
               '--rolling',
               '--output', output_dir,
               '--pages', '1-%s' % limit]
        if lang != 'eng':
            # cf https://github.com/documentcloud/docsplit/issues/72
            # the cleaning functions are only suited for english
            cmd.append('--no-clean')

        self._run_command(cmd)

        # now, move images to correctly named folders
        for name, size in sizes:
            dest = os.path.join(output_dir, name)
            if os.path.exists(dest):
                shutil.rmtree(dest)

            source = os.path.join(output_dir, '%ix' % size)
            shutil.move(source, dest)

    def dump_text(self, filepath, output_dir, ocr, lang='eng'):
        # docsplit text pdf.pdf --[no-]ocr --pages all
        output_dir = os.path.join(output_dir, TEXT_REL_PATHNAME)
        ocr = not ocr and 'no-' or ''
        cmd = [self.binary, "text", filepath,
            '--language', lang,
            '--%socr' % ocr,
            '--pages', 'all',
            '--output', output_dir
        ]
        if lang != 'eng':
            # cf https://github.com/documentcloud/docsplit/issues/72
            # the cleaning functions are only suited for english
            cmd.append('--no-clean')

        self._run_command(cmd)

    def get_num_pages(self, filepath):
        cmd = [self.binary, "length", filepath]
        return int(self._run_command(cmd).strip())

    def convert_to_pdf(self, filepath, filename, output_dir):
        # get ext from filename
        ext = os.path.splitext(os.path.normcase(filename))[1][1:]
        inputfilepath = os.path.join(output_dir, 'dump.%s' % ext)
        shutil.move(filepath, inputfilepath)
        orig_files = set(os.listdir(output_dir))
        cmd = [self.binary, 'pdf', inputfilepath,
            '--output', output_dir]
        self._run_command(cmd)

        # remove original
        os.remove(inputfilepath)

        # while using libreoffice, docsplit leaves a 'libreoffice'
        # folder next to the generated PDF, removes it!
        libreOfficePath = os.path.join(output_dir, 'libreoffice')
        if os.path.exists(libreOfficePath):
            shutil.rmtree(libreOfficePath)

        # move the file to the right location now
        files = set(os.listdir(output_dir))

        if len(files) != len(orig_files):
            # we should have the same number of files as when we first began
            # since we removed libreoffice.
            # We do this in order to keep track of the files being created
            # and used...
            raise Exception("Error converting to pdf")

        converted_path = os.path.join(output_dir,
                                      [f for f in files - orig_files][0])
        shutil.move(converted_path, os.path.join(output_dir, DUMP_FILENAME))

    def convert(self, output_dir, inputfilepath=None, filedata=None,
                converttopdf=False, sizes=(('large', 1000),), enable_indexation=True,
                ocr=True, detect_text=True, format='gif', filename=None, language='eng'):
        if inputfilepath is None and filedata is None:
            raise Exception("Must provide either filepath or filedata params")

        path = os.path.join(output_dir, DUMP_FILENAME)
        if os.path.exists(path):
            os.remove(path)

        if inputfilepath is not None:
            # copy file to be able to work with.
            shutil.copy(inputfilepath, path)
        else:
            fi = open(path, 'wb')
            fi.write(filedata)
            fi.close()

        if converttopdf:
            self.convert_to_pdf(path, filename, output_dir)

        self.dump_images(path, output_dir, sizes, format, language)
        if enable_indexation and ocr and detect_text and textChecker is not None:
            if textChecker.has(path):
                logger.info('Text already found in pdf. Skipping OCR.')
                ocr = False

        if enable_indexation:
            self.dump_text(path, output_dir, ocr, language)

        num_pages = self.get_num_pages(path)

        os.remove(path)
        return num_pages

    def _findbinary(self):
        if 'PATH' in os.environ:
            path = os.environ['PATH']
            path = path.split(os.pathsep)
        else:
            path = self.default_paths

        for directory in path:
            fullname = os.path.join(directory, self.bin_name)
            if os.path.exists(fullname):
                return fullname

        return None

    def _run_command(self, cmd):
        if isinstance(cmd, basestring):
            cmd = cmd.split()
        cmdformatted = ' '.join(cmd)
        logger.info("Running command %s" % cmdformatted)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, close_fds=self.close_fds)
        output, error = process.communicate()
        process.stdout.close()
        process.stderr.close()
        if process.returncode != 0:
            error = """Command
%s
finished with return code
%i
and output:
%s
%s""" % (cmdformatted, process.returncode, output, error)
            logger.info(error)
            raise Exception(error)
        logger.info("Finished Running Command %s" % cmdformatted)
        return output
