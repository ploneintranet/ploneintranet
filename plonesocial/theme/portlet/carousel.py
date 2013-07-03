from zope.interface import implements
from zope.component import getMultiAdapter, getUtility
from AccessControl import getSecurityManager

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from plone.memoize.instance import memoize

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberMultiSelectionWidget

from plone.i18n.normalizer.interfaces import IIDNormalizer

from zope.component.hooks import getSite
import uuid, hashlib

class ICarouselPortlet(IPortletDataProvider):

    images = schema.List(
            title=u'Images',
            required=True,
            value_type=schema.Choice(
                source=SearchableTextSourceBinder(
                    {'portal_type': 'Image'}
                )
            )
    )

    width = schema.Int(
        title=u'Image scale width',
        required=True,
        default=1170
    )

    height = schema.Int(
        title=u'Image scale height',
        required=True,
        default=200
    )

    enable_caption = schema.Bool(
        title=u'Show caption',
        required=False,
        default=False
    )


class Assignment(base.Assignment):
    implements(ICarouselPortlet)

    images = []
    title = u'Carousel portlet'
    width = 1170
    height = 200
    enable_caption = False

    def __init__(self, images=None, width=1170, height=200, enable_caption=False):
        self.images = images or []
        self.width = width
        self.height = height
        self.enable_caption = enable_caption

class Renderer(base.Renderer):
    render = ViewPageTemplateFile('carousel.pt')
    
    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    def randId(self):
        return hashlib.md5(str(uuid.uuid4())).hexdigest()

    def images(self):
        result = []
        for path in self.data.images:
            obj = self._traverse_imagepath(path)
            if obj:
                result.append(obj)
        return result

    def _traverse_imagepath(self, path):
        # stolen from plone.app.collection

        if not path:
            return None

        if path.startswith('/'):
            path = path[1:]

        if not path:
            return None

        site = getSite()
        if isinstance(path, unicode):
            path = str(path)

        result = site.unrestrictedTraverse(path, default=None)
        if result is not None:
            sm = getSecurityManager()
            if not sm.checkPermission('View', result):
                return None

        return result

class AddForm(base.AddForm):
    form_fields = form.Fields(ICarouselPortlet)
    form_fields['images'].custom_widget = UberMultiSelectionWidget
    label = u'Add carousel portlet'
    description = (u'This portlet display an image carousel using Bootstrap '
                    'Carousel')

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(ICarouselPortlet)
    form_fields['images'].custom_widget = UberMultiSelectionWidget
    label = u'Add carousel portlet'
    description = (u'This portlet display an image carousel using Bootstrap '
                    'Carousel')

