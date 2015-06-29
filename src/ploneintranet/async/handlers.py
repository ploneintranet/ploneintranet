import logging

from ploneintranet import api as pi_api
from ploneintranet.async.interfaces import IPloneintranetAsyncLayer

logger = logging.getLogger(__name__)


def generate_attachment_preview_images(obj, event):
    """
    Event handler for generating previews when new content is created
    """
    request = event.object.REQUEST
    if not IPloneintranetAsyncLayer.providedBy(request):
        logger.warn('ploneintranet.async profile not installed. '
                    'Skipping automatic preview generation')
        return

    pi_api.previews.create(obj, request)
