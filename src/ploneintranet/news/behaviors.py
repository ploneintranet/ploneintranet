# -*- coding: utf-8 -*-
from plone.app.vocabularies.catalog import CatalogSource
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from z3c.relationfield.schema import RelationChoice
from zope.interface import provider

from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.news.content import INewsSection


@provider(IFormFieldProvider)
class ISectionReference(form.Schema):
    """A News Item reference to a news section, instead of containment.
    """

    section = RelationChoice(
        title=_(u"Section"),
        source=CatalogSource(
            object_provides=INewsSection.__identifier__),
        required=False,
    )
