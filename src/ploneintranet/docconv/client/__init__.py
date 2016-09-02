# from Products.CMFCore.utils import getToolByName
from collective.documentviewer.convert import Converter
from collective.documentviewer.settings import GlobalSettings
from logging import getLogger
from zope.component.hooks import getSite

logger = getLogger(__name__)

SUPPORTED_CONTENTTYPES = [
    'File',
]

HTML_CONTENTTYPES = [
    'Document'
]


# documentviewer does set the layout in two places. One can be turned off
# the following one can't. So we have to patch.
def _handle_layout(self):
    """
    Deactivate the layout setting part of documentviewer as we want our own
    """
    pass

Converter.handle_layout = _handle_layout


def initialize(context):
    """Initializer called when used as a Zope 2 product."""


def is_autoconv_enabled():
    """
    if enabled, viewing items without a preview will trigger generation
    of a preview
    """
    gsettings = GlobalSettings(getSite())
    return gsettings.auto_convert
