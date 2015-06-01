import logging
from zest.releaser.utils import execute_command

logger = logging.getLogger('ploneintranet.core.release')


def add_files_to_release(data):
    """zest.releaser entry point for adding files to the release."""
    if data.get('name') != 'ploneintranet':
        # This entry point should only do something when releasing the
        # ploneintranet package.
        return
    # cd to the directory that has the fresh tag checkout and use the
    # Makefile to fetch the release bundles.
    logger.info('Making fetchrelease call in tag checkout.')
    res = execute_command('cd {0} && make fetchrelease'.format(data['tagdir']))
    print(res)
    logger.info('fetchrelease done.')
