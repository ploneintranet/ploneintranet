# -*- coding: utf-8 -*-
from plone.app.vocabularies.catalog import CatalogSource
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from z3c.relationfield.schema import RelationChoice
from zope.interface import provider
from zope import schema

from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.news.content import INewsSection


@provider(IFormFieldProvider)
class INewsMeta(form.Schema):
    """Extra newsitem metadata for magazine
    """

    # A News Item reference to a news section, instead of containment.
    section = RelationChoice(
        title=_(u"Section"),
        source=CatalogSource(
            object_provides=INewsSection.__identifier__),
        required=False,
    )

    article_image = schema.Bool(
        title=_(
            u'label_article_image',
            default=u'Image visible as hero image on the news article page.'
        ),
        required=False,
        default=True,
    )

    magazine_image = schema.Bool(
        title=_(
            u'label_magazine_image',
            default=u'Image visible on news overview pages.'
        ),
        required=False,
        default=True,
    )

    magazine_home = schema.Bool(
        title=_(
            u'label_magazine_home',
            default=u'Visible on news landing page'
        ),
        required=False,
        default=True,
    )

    # commenting not implemented yet
    allow_comments = schema.Bool(
        title=_(
            u'label_allow_comments',
            default=u'Allow comments'
        ),
        required=False,
        default=True,
    )

    def sections(self):
        return self.aq_parent.sections()
