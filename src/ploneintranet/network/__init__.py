# -*- coding: utf-8 -*-
from Products.PlonePAS import config as plonepas_config
import logging

logger = logging.getLogger(__name__)

# monkey Products.PlonePAS image scales
# until PLIP 12870 is merged
logger.info('Setting PlonePAS portrait scale')
plonepas_config.MEMBER_IMAGE_SCALE = portrait_scale = (300, 300)
plonepas_config.IMAGE_SCALE_PARAMS['scale'] = portrait_scale


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
