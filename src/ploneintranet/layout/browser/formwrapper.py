# coding=utf-8
from pkg_resources import resource_filename
from ploneintranet.layout.interfaces import IPloneintranetFormLayer
import plone.z3cform


layout_factory = plone.z3cform.templates.ZopeTwoFormTemplateFactory(
    resource_filename(
        'ploneintranet.layout.browser',
        'templates/formwrapper.pt'
    ),
    form=plone.z3cform.interfaces.IFormWrapper,
    request=IPloneintranetFormLayer,
)
