import logging

from ploneintranet import api as pi_api

logger = logging.getLogger(__name__)


def generate_attachment_preview_images(obj, event):
    """
    Event handler for generating previews when new content is created
    """
    pi_api.previews.create(obj, event.object.REQUEST)
