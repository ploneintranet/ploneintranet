import logging
from pathlib import Path
import subprocess

from plone.protect.interfaces import IDisableCSRFProtection
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.Five import BrowserView
from zope.interface import alsoProvides
import os

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
        raise
    return output.decode('utf-8').splitlines()


class ConvertDocument(BrowserView):
    """Convert a document to pdf and preview images.

    Meant to be called from a Celery task.

    Note that we explicitly disable CSRF protection.  There is no form
    that we can fill in, so there is no authenticator token that we
    could check.  Alternative: create such a form anyway, GET it from
    a Celery task, parse the html to get the authenticator token, and
    POST to the form again.  Seems overkill.
    """
    bin_name = 'docsplit'

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        # Get the file data of the context object
        primary_field = IPrimaryFieldInfo(self.context).value
        data = bytes(primary_field.data)

        # Create the temporary storage location if it doesn't exist
        # TODO: This should probably configurable (registry)
        storage_dir = Path('/tmp/ploneintranet-docconv')
        if not storage_dir.exists():
            storage_dir.mkdir(parents=True)

        # Write file data to temporary file
        input_file = storage_dir.joinpath('{}.tmp'.format(self.context.id))
        with open(str(input_file)) as fd:
            fd.write(data)

        output_dir = storage_dir.joinpath(
            '{}-converted'.format(self.context.id))
        if not output_dir.exists():
            output_dir.mkdir(parents=True)
        # XXX; This is possibly not needed, as all we're interested in is the
        # preview images. Keeping it commented for now, just in case.
        # Generate the PDFs
        # cmd = [self.binary, 'pdf', input_file,
        #        '--output', output_dir]
        # pdf_cmd_output = self._parse_cmd_output(cmd)

        # Generate the image previews
        # TODO: Sizes might want to be configurable
        # TODO: Page count might want to be configurable
        cmd = [
            self.binary,
            'images', input_file,
            '--size', '180,700,1000',
            '--format', 'png',
            '--rolling',
            '--output', output_dir,
            '--pages', '1-20']
        cmd_output = _parse_cmd_output(cmd)

        # Attach the previews to the context as annotations

        return cmd_output

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
