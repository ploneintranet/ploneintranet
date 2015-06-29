from base64 import b64encode
import logging
import subprocess

from pathlib import Path
from plone.protect.interfaces import IDisableCSRFProtection
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.Five import BrowserView
from zope.interface import alsoProvides

import os
from ploneintranet import api as pi_api

logger = logging.getLogger(__name__)


def _parse_cmd_output(cmd):
    """
    Run the given arguments as a subprocess, and spilt the output into
    lines

    :param cmd: The command arguments to run
    :type cmd: list
    :return: The parsed output
    :rtype: list
    """
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logger.error('Failed to pass command %s', ' '.join(cmd))
        logger.error('Output was %s', e.output)
        raise e
    except OSError as e:
        logger.exception('Failed to pass command %s', ' '.join(cmd))
        logger.exception('Exception was %s', e)
        raise e
    return output.decode('utf-8').splitlines()


class BaseDocConvView(BrowserView):
    bin_name = 'docsplit'

    def input_file(self):
        """Extract the contents of the object to be converted, and save to a
        temporary file

        :return: The temporary file
        :rtype: file
        """
        try:
            primary_field = IPrimaryFieldInfo(self.context).value
        except TypeError:
            return
        if primary_field is None:
            return
        data = bytes(primary_field.data)
        input_file = self.storage_dir.joinpath(
            '{}.tmp'.format(self.context.id))
        with open(str(input_file), 'wb') as fd:
            fd.write(data)
        return input_file

    def _find_binary(self):
        """
        Attempt to find fullpath to docsplit binary

        :return: The fullpath to the docsplit binary
        :rtype: str
        """
        path = os.getenv('PATH', '/bin:/usr/bin:/usr/local/bin')

        for directory in path.split(os.pathsep):
            fullname = Path(directory).joinpath(self.bin_name)
            if fullname.exists():
                return str(fullname)

        return self.bin_name

    @property
    def storage_dir(self):
        """Find or create temporary directory to be used by docsplit

        :return: The temporary directory
        :rtype: :class:`pathlib.Path`
        """
        # TODO: This should probably configurable (registry)
        storage_dir = Path('/tmp/ploneintranet-docconv')
        if not storage_dir.exists():
            storage_dir.mkdir(parents=True)

        return storage_dir

    @property
    def output_dir(self):
        """Find or create an output directory

        :return: The output directory
        :rtype: :class:`pathlib.Path`
        """
        output_dir = self.storage_dir.joinpath(
            '{}-converted'.format(self.context.id))
        if not output_dir.exists():
            output_dir.mkdir(parents=True)

        return output_dir


class GeneratePreviewImages(BaseDocConvView):
    """Generate preview images for a piece of content

    Meant to be called from a Celery task.

    Note that we explicitly disable CSRF protection.  There is no form
    that we can fill in, so there is no authenticator token that we
    could check.  Alternative: create such a form anyway, GET it from
    a Celery task, parse the html to get the authenticator token, and
    POST to the form again.  Seems overkill.
    """

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        input_file = self.input_file()
        if input_file is None:
            return
        cmd = [
            self._find_binary(),
            'images', str(input_file),
            '--size', '1000',
            '--format', 'png',
            '--output', str(self.output_dir),
        ]
        cmd_output = _parse_cmd_output(cmd)
        for image in self.output_dir.iterdir():
            with open(str(image)) as fd:
                pi_api.attachments.add(
                    self.context,
                    'preview_{0}'.format(image.name),
                    fd.read())
            image.unlink()
        self.output_dir.rmdir()

        return 'Command output: {}'.format(cmd_output)


class GeneratePDF(BaseDocConvView):
    """Generate PDFs of a piece of content

    Meant to be called by a Celery task
    """

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        input_file = self.input_file()
        if input_file is None:
            return
        cmd = [
            self._find_binary(),
            'pdf', str(input_file),
            '--output', str(self.output_dir),
        ]
        cmd_output = _parse_cmd_output(cmd)

        return 'Command output: {}'.format(cmd_output)


class GenerateAttachmentThumbnail(BaseDocConvView):
    """Generate first page, low-res attachment preview for status update

    This view is meant to be called synchronously from the AJAX call made when
    selecting attachments during status update composition
    """
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        uploaded_attachments = self.request.get('form.widgets.attachments', [])
        if not isinstance(uploaded_attachments, list):
            uploaded_attachments = [uploaded_attachments]
        for file_field in uploaded_attachments:
            data = file_field.read()
            input_file = self.storage_dir.joinpath(
                '{}.tmp'.format(file_field.filename))
            with open(str(input_file), 'wb') as fd:
                fd.write(data)
            cmd = [
                self._find_binary(),
                'images', str(input_file),
                '--size', '128',
                '--format', 'png',
                '--output', str(self.output_dir),
                '--pages', '1'
            ]
            cmd_output = _parse_cmd_output(cmd)

        base64_img_data = []
        for image in self.output_dir.iterdir():
            with open(str(image)) as fd:
                data = fd.read()
                base64_img_data.append(b64encode(data))
            image.unlink()
        self.output_dir.rmdir()
        return base64_img_data
