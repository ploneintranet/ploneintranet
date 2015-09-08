from collective.documentviewer.convert import Converter as DVConverter
from logging import getLogger

log = getLogger(__name__)


class Converter(DVConverter):

    def handle_layout(self):
        """
        Deactivate the layout setting part of documentviewer as we want our own
        """
        pass
