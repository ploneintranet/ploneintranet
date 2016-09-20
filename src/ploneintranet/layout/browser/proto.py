# coding=utf-8
from logging import getLogger
from plone.memoize import forever
from Products.Five import BrowserView

logger = getLogger(__name__)


class ProtoView(BrowserView):
    ''' A view that contains prototype related utilities
    '''
    @forever.memoize
    def translate_friendly_type(self, value):
        ''' Translate the Plone intranet friendly_type_name into a
        name that fits the prototype conventions
        '''
        value = value.lower()
        if 'word' in value or 'odt document' in value:
            return 'word'
        if 'excel' in value or 'ods spreadsheet' in value:
            return 'excel'
        if 'pdf' in value:
            return 'pdf'
        if 'page' in value:
            return 'rich'
        if 'news' in value:
            return 'news'
        if 'event' in value:
            return 'event'
        if 'image' in value:
            return 'image'
        if 'presentation' in value:
            return 'powerpoint'
        if 'workspace' in value:
            return 'workspace'
        if 'link' in value:
            return 'link'
        if 'question' in value:
            return 'question'
        if 'audio' in value:
            return 'audio'
        if 'video' in value:
            return 'video'
        if 'contract' in value:
            return 'contract'
        if 'odt' in value:
            return 'odt'
        if 'document' in value:
            return 'odt'
        if 'openoffice' in value:
            return 'odt'
        if 'octet' in value:
            return 'octet'
        if 'postscript' in value:
            return 'postscript'
        if 'plain' in value:
            return 'plain-text'
        if 'archive' in value:
            return 'zip'
        if 'business card' in value:
            return 'business-card'
        if 'userprofilecontainer' in value:
            return 'folder'
        if 'todo' in value:
            return 'task'
        if 'folder' in value:
            return 'folder'
        if 'library.section' in value:
            return 'library-section'
        if 'library.folder' in value:
            return 'library-subsection'
        # we don't have a way to distinguish Document in library yet
        # that would become 'library-item
        if 'superspace' in value:
            return 'superspace'
        if 'app' in value:
            return 'app'
        if 'email' in value or 'e-mail' in value:
            return 'email'
        if 'profile' in value or 'person' in value:
            return 'people'
        # This is our fallback
        logger.warn('Unrecognized friendly type: %s', value)
        return 'file'

    @forever.memoize
    def friendly_type2type_class(self, value):
        ''' Take the friendly type name and return a class for displaying
        the correct type.
        '''
        proto_type = self.translate_friendly_type(value)
        return 'type-%s' % proto_type

    @forever.memoize
    def friendly_type2icon_class(self, value):
        ''' Take the friendly type name (e.g. OpenOffice Write Document)
        and return a class for displaying the correct icon.
        '''
        proto_type = self.translate_friendly_type(value)
        # files -> .icon-file-audio etc...
        if proto_type in (
            'archive',
            'audio',
            'code',
            'excel',
            'image',
            'pdf',
            'powerpoint',
            'video',
            'word',
        ):
            return 'icon-file-%s' % proto_type
        # known documents
        if proto_type in (
            'app',
            'email',
            'workspace',
            'folder',
            'link',
            'document',
        ):
            return 'icon-%s' % proto_type
        if proto_type == 'rich':
            return 'icon-doc-text'
        if proto_type == 'people':
            return 'icon-user'
        if proto_type == 'file':
            return 'icon-document'

        logger.warn('Cannot assign an icon class for: %s', value)
        return 'icon-document'
