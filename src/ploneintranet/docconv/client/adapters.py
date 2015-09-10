from plone import api
from zope.site.hooks import getSite

from collective.documentviewer.settings import Settings
from collective.documentviewer.settings import GlobalSettings
from collective.documentviewer import storage
from collective.documentviewer.convert import DUMP_FILENAME
from collective.documentviewer.convert import TEXT_REL_PATHNAME
from collective.documentviewer.browser.views import DocumentViewerView
from DateTime import DateTime

from Products.CMFCore.utils import getToolByName

from .handlers import handle_file_creation


class PIDocumentViewerView(DocumentViewerView):

    def __init__(self, context, request=None):
        super(PIDocumentViewerView, self).__init__(context, request)
        self.site = getSite()
        self.global_settings = GlobalSettings(self.site)
        self.settings = Settings(self.context)
        self.portal_url = self.site.portal_url()

        resource_url = self.global_settings.override_base_resource_url
        rel_url = storage.getResourceRelURL(gsettings=self.global_settings,
                                            settings=self.settings)
        if resource_url:
            self.dvpdffiles = '%s/%s' % (resource_url.rstrip('/'),
                                         rel_url)
        else:
            self.dvpdffiles = '%s/%s' % (self.portal_url, rel_url)

    def dv_data(self):
        """ Originally taken from c.documentviewer.views.DocumentViewView
            It expects that all objects are in the classical containment
            hierarchy, which is not true for attachments at the moment
            so we are customising it here
        """
        dump_path = DUMP_FILENAME.rsplit('.', 1)[0]
        if self.global_settings.override_contributor:
            contributor = self.global_settings.override_contributor
        else:
            contributor = self.context.Creator()

        mtool = getToolByName(self.site, 'portal_membership')
        contributor_user = mtool.getMemberById(contributor)
        if contributor_user is not None:
            contributor = contributor_user.getProperty('fullname', None) \
                or contributor

        contributor = '<span class="DV-Contributor">%s</span>' % contributor

        if self.global_settings.override_organization:
            organization = self.global_settings.override_organization
        else:
            organization = self.site.title

        organization = '<span class="DV-Organization">%s</span>' % organization
        image_format = self.settings.pdf_image_format
        if not image_format:
            # oops, this wasn't set like it should have been
            # on alpha release. We'll default back to global
            # setting.
            image_format = self.global_settings.pdf_image_format

        try:
            canonical_url = self.context.absolute_url()
        except AttributeError:
            canonical_url = ''  # XXX construct a url to an attachment

        return {
            'access': 'public',
            'annotations': self.annotations(),
            'sections': list(self.sections()),
            'canonical_url': canonical_url + '/view',
            'created_at': DateTime(self.context.CreationDate()).aCommonZ(),
            'data': {},
            'description': self.context.Description(),
            'id': self.context.UID(),
            'pages': self.settings.num_pages,
            'updated_at': DateTime(self.context.ModificationDate()).aCommonZ(),
            'title': self.context.Title(),
            'source': '',
            "contributor": contributor,
            "contributor_organization": organization,
            'resources': {
                'page': {
                    'image': '%s/{size}/%s_{page}.%s' % (
                        self.dvpdffiles, dump_path,
                        image_format),
                    'text': '%s/%s/%s_{page}.txt' % (
                        self.dvpdffiles, TEXT_REL_PATHNAME, dump_path)
                },
                'pdf': canonical_url,
                'thumbnail': '%s/small/%s_1.%s' % (
                    self.dvpdffiles, dump_path,
                    image_format),
                'search': '%s/dv-search.json?q={query}' % (
                    canonical_url)
            }
        }


class DocconvAdapter(object):
    """ """

    def __init__(self, context, request=None):
        self.site = getSite()
        self.context = context
        if request is not None:
            self.request = request
        elif hasattr(self.context, 'REQUEST'):
            self.request = self.context.REQUEST
        elif hasattr(self.context, 'request'):
            self.request = self.context.request
        else:
            self.request = api.portal.getRequest()

        self.global_settings = GlobalSettings(self.site)
        self.settings = Settings(self.context)
        self.dvview = PIDocumentViewerView(self.context, self.request)

        # self.dvview = getMultiAdapter((self.context, self.request),
        #                               name="documentviewer")
        # self.dvview.global_settings = self.global_settings
        # self.dvview.settings = self.settings
        # self.dvview.site = self.site

        self.data = self.dvview.dv_data()

    def get_number_of_pages(self, img_type='preview'):
        return self.data.get('pages', -1)

    def is_available(self, data_type='preview'):
        """
        Try to determine if the asked preview type is available
        If not, schedule a conversion
        """
        if data_type == 'pdf':
            return 'pdf' in self.data['resources']

        if data_type not in ('large', 'normal', 'small'):
            data_type = 'normal'
        file_type = '%s/dump_1.%s' % (data_type,
                                      self.settings.pdf_image_format)

        if file_type in self.settings.blob_files:
            return True

        if self.global_settings.auto_convert and \
           self.settings.successfully_converted is not True:
                # MAKE THIS ASYNC
                handle_file_creation(self.context)
        return False

    def has_pdf(self):
        return 'pdf' in self.data['resources']

    def has_previews(self):
        if not self.settings.blob_files:
            return False
        return len(self.settings.blob_files) > 0

    def has_thumbs(self):
        return self.has_previews()

    def conversion_message(self):
        if self.settings.successfully_converted is False:
            return self.settings.exception_msg
        elif self.settings.converting is True:
            return u"Still converting."
        else:
            return u"Document converted successfully"

    def get_pdf(self):
        if self.has_pdf:
            return self.data['resources']['pdf']
        return ''

    def get_previews(self, size='normal'):
        if self.has_previews():
            previews = []
            tpl = self.data['resources']['page']['image']
            for i in range(self.data['pages']):
                previews.append(tpl.replace('{size}', size)
                                   .replace('{page}', str(i + 1)))
            return previews
        return None

    def get_thumbs(self):
        if self.has_thumbs():
            return (self.data['resources']['thumbnail'],)
        return None

    def generate_all(self):
        # Make this ASYNC
        return handle_file_creation(self.context)
