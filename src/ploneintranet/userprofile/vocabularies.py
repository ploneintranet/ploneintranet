from zope.schema.vocabulary import SimpleVocabulary

from plone import api as plone_api


def primaryLocationVocabulary(context):
    locations = plone_api.portal.get_registry_record(
        'ploneintranet.userprofile.locations')
    return SimpleVocabulary.fromValues(locations)
